"""
NexTool API Proxy - Afdian Webhook
爱发电付款回调 → 自动生成 Pro 密钥
Vercel Serverless Function
"""

import os
import json
import time
from datetime import datetime

from _kv import _kv_get, _kv_set, _kv_set_nx, KVError
from _pro_keys import (KEY_PREFIX, ORDER_PREFIX, ORDER_TTL_SECONDS,
                       generate_pro_key, _expiry_for, _plan_duration_days,
                       _key_ttl_seconds)

AFDIAN_TOKEN = os.environ.get("AFDIAN_TOKEN", "")

# 弱 token 等于没有验签。启动即拒绝，而不是等到有人伪造付款。
if AFDIAN_TOKEN and len(AFDIAN_TOKEN) < 16:
    raise RuntimeError(
        "AFDIAN_TOKEN 长度只有 %d，低于 16 字符下限。"
        "弱 token 等于没有验签——请改用随机生成的长 token。"
        % len(AFDIAN_TOKEN)
    )

_CORS = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}


def handler(request):
    if request.method == "OPTIONS":
        return {
            "status_code": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    if request.method != "POST":
        return {
            "status_code": 405,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Method not allowed"}),
        }

    try:
        body = request.json() if hasattr(request, "json") else json.loads(request.body or "{}")
    except Exception:
        return {
            "status_code": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Invalid JSON"}),
        }

    # 验签：配置缺失时 fail-closed。
    # 原代码是 `if AFDIAN_TOKEN:`——未配置就整段跳过，任何人都能POST
    # 一个伪造的 {"order": {...}} 白拿一个真密钥。
    if not AFDIAN_TOKEN:
        return {
            "status_code": 503,
            "headers": _CORS,
            "body": json.dumps({
                "error": "server_not_configured",
                "detail": "AFDIAN_TOKEN 未配置，无法验签。拒绝处理 webhook，"
                          "否则任何人都能伪造付款回调领取密钥。",
            }),
        }

    received_token = body.get("token", "")
    if received_token != AFDIAN_TOKEN:
        return {
            "status_code": 403,
            "headers": _CORS,
            "body": json.dumps({"error": "Invalid Afdian token"}),
        }

    # 防重放：抓包重放同一个 payload 可以反复领key。
    ts = body.get("timestamp", "")
    if ts:
        try:
            if abs(time.time() - int(ts)) > 300:
                return {
                    "status_code": 403,
                    "headers": _CORS,
                    "body": json.dumps({"error": "Request timestamp out of window"}),
                }
        except (TypeError, ValueError):
            return {
                "status_code": 403,
                "headers": _CORS,
                "body": json.dumps({"error": "Invalid timestamp"}),
            }

    # Parse order data
    order = body.get("order", {})
    order_id = order.get("order_id", "")
    user_id = order.get("user_id", "")
    email = order.get("email", "")
    amount = order.get("total_amount", "0")
    status = order.get("status", "")

    # Only process successful payments
    if status not in (1, "1", "active"):
        return {
            "status_code": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps({"status": "ignored", "reason": f"order status: {status}"}),
        }

    # 幂等：用 SET NX 抢占。
    # 为什么这次能真正生效——原先读的是 PRO_KEYS_JSON 这个只读环境变量的
    # 解析结果（进程内局部变量，写了也丢），所以「已处理」判断永远为False，
    # 重复回调每次都生成一个新密钥。
    # 现在写的是 Redis，SET NX 由Redis 单线程串行执行，并发到达时
    # 必然只有一个抢到——不需要 WATCH/MULTI、Lua 或分布式锁。
    order_key = ORDER_PREFIX + order_id
    try:
        claimed = _kv_set_nx(order_key, {"key": "", "status": "claimed"},
                             ttl=ORDER_TTL_SECONDS)
    except KVError as exc:
        return {
            "status_code": 503,
            "headers": _CORS,
            "body": json.dumps({"error": "storage_unavailable", "detail": str(exc)[:200]}),
        }

    if not claimed:
        existing = _kv_get(order_key) or {}
        return {
            "status_code": 200,
            "headers": _CORS,
            "body": json.dumps({
                "status": "already_processed",
                "key": existing.get("key", ""),
            }),
        }

    # Determine plan duration
    plan_name = str(order.get("plan", "")).lower()
    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        amount_value = 0.0
    if "year" in plan_name or amount_value >= 100:
        plan = "yearly"
    elif "lifetime" in plan_name:
        plan = "lifetime"
    else:
        plan = "monthly"

    key = generate_pro_key()
    expires_at = _expiry_for(plan)

    try:
        _kv_set(KEY_PREFIX + key, {
            "plan": plan,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
        }, ttl=_key_ttl_seconds(expires_at))

        # 补全抢占记录：同一order_key 覆盖写。幂等性已由上面的 NX 保证——
        # 能走到这里的只有唯一那个执行者，所以覆盖是安全的。
        _kv_set(order_key, {
            "key": key,
            "plan": plan,
            "email": email,
            "amount": amount,
            "created_at": datetime.now().isoformat(),
        }, ttl=ORDER_TTL_SECONDS)
    except KVError as exc:
        return {
            "status_code": 503,
            "headers": _CORS,
            "body": json.dumps({"error": "storage_unavailable", "detail": str(exc)[:200]}),
        }



    return {
        "status_code": 200,
        "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
        "body": json.dumps({
            "status": "success",
            "key": key,
            "plan": plan,
            "expires_at": expires_at,
            "message": f"感谢支持！您的Pro密钥: {key}，请在工具页面输入此密钥解锁Pro功能。",
        }),
    }
