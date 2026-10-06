"""
NexTool API Proxy - Pro Key Verification
Vercel Serverless Function

密钥存放在 Upstash Redis，不再用环境变量里的一个 JSON。
原先的 PRO_KEYS_JSON 方案有两个硬伤：Vercel 环境变量上限 64KB
（实测每条记录约 403 字节，约 162 个付费用户就撑爆），而且它是
只读的——webhook 写进去的内容随进程结束蒸发，密钥从未真正落盘。
"""

import json

from _kv import _kv_get, KVError
from _pro_keys import KEY_PREFIX, _looks_like_key

_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


def _check(key):
    """返回 (valid, key_info)。

    key_info 为 None 表示「查不到」；
    key_info 存在但 valid=False 表示「查到了但已过期」——
    调用方据此区分 expired 与 not_found，因为前端要给出不同的提示。
    """
    if not _looks_like_key(key):
        return False, None

    key_info = _kv_get(KEY_PREFIX + key)
    if not isinstance(key_info, dict):
        return False, None

    expires_at = key_info.get("expires_at")
    if expires_at:
        from datetime import datetime
        try:
            expires = datetime.fromisoformat(expires_at)
        except (TypeError, ValueError):
            # 存量数据格式异常时按过期处理，但不要抛异常——
            # 一条脏记录不该让整个接口 500。
            return False, key_info
        if expires < datetime.now():
            return False, key_info

    return True, key_info


def handler(request):
    if request.method == "OPTIONS":
        return {
            "status_code": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
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

    key = body.get("key", "")

    try:
        valid, key_info = _check(key)
    except KVError as exc:
        # 存储不可用必须说成 503，不能谎称「密钥无效」。
        # 前端据此走离线宽限（保留付费身份），而 200+invalid
        # 会让用户以为密钥被删了，重新输入也解决不了。
        return {
            "status_code": 503,
            "headers": _CORS,
            "body": json.dumps({
                "valid": False,
                "reason": "storage_unavailable",
                "detail": str(exc)[:200],
            }),
        }

    if valid and key_info:
        return {
            "status_code": 200,
            "headers": _CORS,
            "body": json.dumps({
                "valid": True,
                "plan": key_info.get("plan", "monthly"),
                "expires_at": key_info.get("expires_at"),
                # 订单备注仅供人工排查，不返回给前端
            }),
        }

    if key_info and key_info.get("expires_at"):
        return {
            "status_code": 200,
            "headers": _CORS,
            "body": json.dumps({
                "valid": False,
                "reason": "expired",
                "expired_at": key_info["expires_at"],
                "plan": key_info.get("plan", "monthly"),
            }),
        }

    return {
        "status_code": 200,
        "headers": _CORS,
        "body": json.dumps({"valid": False, "reason": "not_found"}),
    }