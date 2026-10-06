"""
NexTool API Proxy - Pro Key Activation
Vercel Serverless Function

与 pro-verify共用 _kv 与 _pro_keys。原先本文件持有一份与
pro-verify.py 逐字符相同的 _load_pro_keys() 与 _is_pro_key_valid()，
改一处漏另一处的风险很高，故抽到公共模块。

说明：激活本身不写任何状态。「输入密钥→ 校验→ 写localStorage」
整套动作都在浏览器端完成，服务端只回答这个密钥当前是否有效。
这不是 bug——激活的本质就是验证，无状态是合理的。
"""

import json

from _kv import _kv_get, KVError
from _pro_keys import KEY_PREFIX, _looks_like_key

_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


def _check(key):
    """返回 (valid, key_info)，语义与 pro-verify 的 _check 相同。"""
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
        # 前端据此提示「服务暂时不可用」而非「密钥无效」，
        # 前者用户会稍后重试，后者会让他以为自己被拒了。
        return {
            "status_code": 503,
            "headers": _CORS,
            "body": json.dumps({
                "valid": False,
                "reason": "storage_unavailable",
                "detail": str(exc)[:200],
            }),
        }

    if not valid:
        if key_info and key_info.get("expires_at"):
            return {
                "status_code": 200,
                "headers": _CORS,
                "body": json.dumps({
                    "valid": False,
                    "reason": "expired",
                    "expired_at": key_info["expires_at"],
                }),
            }
        return {
            "status_code": 200,
            "headers": _CORS,
            "body": json.dumps({"valid": False, "reason": "invalid_key"}),
        }

    return {
        "status_code": 200,
        "headers": _CORS,
        "body": json.dumps({
            "valid": True,
            "plan": key_info.get("plan", "monthly"),
            "expires_at": key_info.get("expires_at"),
            "message": "Pro已激活！所有AI工具无限制使用。",
        }),
    }