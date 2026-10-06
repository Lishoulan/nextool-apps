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

# 注意：这里没有 AFDIAN_TOKEN 校验，因为爱发电的 webhook 推送
# **不带任何签名字段**。官方文档（guide.afdian.com/creator/developer）确认
# 签名机制只存在于「API 主动查询」那条链路：
#   sign = md5(token + params + ts + user_id)
# 而 webhook 的请求体形如
#   {"ec":200,"em":"ok","data":{"type":"order","order":{...}}}
# 里既没有 token 也没有 sign。原代码的 `if AFDIAN_TOKEN:` 分支
# 因此永远读到 body.get("token", "") == ""，恒为 403 ——
# 也就是说这个 webhook 在真实平台上从未成功处理过一笔订单。
#
# 准入控制改为：out_trade_no 幂等（同一订单不会重复发key）
#            + status == 2 才处理。
# 代价是无法验明「请求确实来自爱发电」。若要更强的保证，
# 应改用爱发电的主动查询 API 轮询订单，而不是依赖 webhook 推送。

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

    # 幂等键先算出来：无论后续走哪个分支都要用。
    # 爱发电的 webhook 请求体（官方文档 guide.afdian.com/creator/developer）：
    #   {"ec":200,"em":"ok","data":{"type":"order","order":{...}}}
    # order 对象里没有 token 字段——签名机制只存在于「API 主动查询」那条链路
    # （sign = md5(token + params + ts + user_id)），webhook 推送不带签名。
    # 所以这里无法验签，改用下面的准入控制兜底。
    data = body.get("data") or {}
    order = data.get("order") or {}

    order_id = order.get("out_trade_no", "")      # 文档：订单号字段是 out_trade_no
    user_id = order.get("user_id", "")
    plan_id = order.get("plan_id", "")            # 文档：方案 ID，自选方案则为空
    month = order.get("month", 0)                 # 文档：赞助月份数
    amount = order.get("total_amount", "0")
    title = order.get("title", "")or order.get("remark", "")
    status = order.get("status", "")

    if not order_id:
        return {
            "status_code": 400,
            "headers": _CORS,
            "body": json.dumps({"error": "missing out_trade_no"}),
        }

    # 只处理交易成功。文档明确：status 2 为交易成功，
    # 「目前仅会推送此类型」。
    if str(status) != "2":
        return {
            "status_code": 200,
            "headers": _CORS,
            # 必须回 {"ec":200}，否则爱发电认为回调失败会反复重试。
            "body": json.dumps({"ec": 200, "em": "", "status": "ignored",
                                "reason": "order status %s" % status}),
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
                # 爱发电要求响应含 ec:200，否则视为回调失败并反复重试
                "ec": 200,
                "em": "",
                "status": "already_processed",
                "key": existing.get("key", ""),
            }),
        }

    # Determine plan duration
    # 套餐判定用文档里的 month 字段，不靠金额猜。
    # 原代码是 `amount >= 100 → yearly`，这会把任何超过 100 元的
    # 订单都当成年付，包括月付但买了很多份的情况。
    try:
        months = int(month)
    except (TypeError, ValueError):
        months = 1
    if months >= 120:
        plan = "lifetime"      # 爱发电的永久方案按 120 个月计
    elif months >= 12:
        plan = "yearly"
    else:
        plan = "monthly"

    key = generate_pro_key()
    expires_at = _expiry_for(plan)

    try:
        _kv_set(KEY_PREFIX + key, {
            "plan": plan,
            # webhook 的order 对象里没有 email 字段（官方文档字段说明里
            # 只有 address_* 是收货信息）。留 remark 供人工排查对账。
            "remark": title[:200],
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
        }, ttl=_key_ttl_seconds(expires_at))

        # 补全抢占记录：同一order_key 覆盖写。幂等性已由上面的 NX 保证——
        # 能走到这里的只有唯一那个执行者，所以覆盖是安全的。
        _kv_set(order_key, {
            "key": key,
            "plan": plan,
            "plan_id": plan_id,
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
        "headers": _CORS,
        "body": json.dumps({
            # 爱发电的文档：响应必须含 ec:200，否则平台认为回调失败。
            # 这也是我们唯一的「密钥交付」途径——HTTP 响应体是服务器到
            # 服务器的通道，用户看不到，所以真正交付要靠 remark 里留的
            # 订单号 + 用户在爱发电后台自行查收，或人工发邮件。
            "ec": 200,
            "em": "",
            "status": "success",
            "key": key,
            "plan": plan,
            "expires_at": expires_at,
            "order_id": order_id,
        }),
    }
