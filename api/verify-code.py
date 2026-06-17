"""NextTool 兑换码验证与使用 API

GET  /api/verify-code?code=NT-PRO-XXXXXXXX  验证兑换码是否有效
POST /api/verify-code                        使用兑换码（标记为已使用）

兑换码存储在内存中（生产环境应使用 Vercel KV）。
通过 afdian-webhook 生成的兑换码会自动存入此存储。
也支持从 codes.json 预加载兑换码。
"""

import os
import json
import time

# 兑换码内存存储
_codes_store: dict = {}

# 预加载 codes.json 中的兑换码（如果存在）
_CODES_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "codes.json")


def _load_codes():
    """从 codes.json 加载预生成的兑换码（兼容数组和对象两种 JSON 格式）"""
    global _codes_store
    if _codes_store:
        return  # 已加载则跳过

    try:
        if os.path.exists(_CODES_JSON_PATH):
            with open(_CODES_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 兼容数组格式 [{...}, ...] 和对象格式 {"codes": [{...}, ...]}
                if isinstance(data, list):
                    codes_list = data
                elif isinstance(data, dict):
                    codes_list = data.get("codes", [])
                else:
                    codes_list = []
                for code_entry in codes_list:
                    code = code_entry.get("code", "")
                    if code and code not in _codes_store:
                        _codes_store[code] = code_entry
    except Exception:
        pass


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def handler(request):
    """Vercel Python serverless function handler"""

    # 加载兑换码
    _load_codes()

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return {
            "status_code": 200,
            "headers": _cors_headers(),
            "body": "",
        }

    # GET: 验证兑换码
    if request.method == "GET":
        return _handle_verify(request)

    # POST: 使用兑换码
    if request.method == "POST":
        return _handle_redeem(request)

    return {
        "status_code": 405,
        "headers": {**_cors_headers(), "Content-Type": "application/json"},
        "body": json.dumps({"error": "Method not allowed. Use GET or POST."}),
    }


def _handle_verify(request):
    """GET /api/verify-code?code=NT-PRO-XXXXXXXX

    验证兑换码是否有效，返回兑换码信息（不标记为已使用）。
    """
    # 获取兑换码参数
    code = ""
    if hasattr(request, "args"):
        code = request.args.get("code", "")
    elif hasattr(request, "query"):
        query = request.query or ""
        if "code=" in query:
            for param in query.split("&"):
                if param.startswith("code="):
                    code = param.split("=", 1)[1]
                    break

    # 也支持从 URL path 或 headers 获取
    if not code and hasattr(request, "headers"):
        code = request.headers.get("x-code", "")

    if not code:
        return {
            "status_code": 400,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing code parameter. Use ?code=NT-PRO-XXXXXXXX"}),
        }

    # 查找兑换码
    code_upper = code.upper().strip()
    entry = _codes_store.get(code_upper)

    if not entry:
        return {
            "status_code": 404,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({
                "valid": False,
                "error": "Code not found",
            }),
        }

    if entry.get("used", False):
        return {
            "status_code": 200,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({
                "valid": False,
                "error": "Code already used",
                "used_at": entry.get("used_at"),
                "used_by": entry.get("used_by"),
            }),
        }

    return {
        "status_code": 200,
        "headers": {**_cors_headers(), "Content-Type": "application/json"},
        "body": json.dumps({
            "valid": True,
            "plan": entry.get("plan", "pro"),
            "plan_name": entry.get("plan_name", "专业版"),
            "source": entry.get("source", "manual"),
        }),
    }


def _handle_redeem(request):
    """POST /api/verify-code

    使用兑换码，标记为已使用。
    Body: {"code": "NT-PRO-XXXXXXXX", "email": "user@example.com"}
    """
    try:
        if hasattr(request, "json"):
            body = request.json() if callable(request.json) else request.json
        elif hasattr(request, "body"):
            raw = request.body or b""
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            body = json.loads(raw) if raw else {}
        else:
            body = {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {
            "status_code": 400,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    code = body.get("code", "").upper().strip()
    email = body.get("email", "").strip()

    if not code:
        return {
            "status_code": 400,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing code field"}),
        }

    # 查找兑换码
    entry = _codes_store.get(code)

    if not entry:
        return {
            "status_code": 404,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({
                "success": False,
                "error": "Code not found",
            }),
        }

    if entry.get("used", False):
        return {
            "status_code": 200,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({
                "success": False,
                "error": "Code already used",
                "used_at": entry.get("used_at"),
            }),
        }

    # 标记为已使用
    entry["used"] = True
    entry["used_at"] = int(time.time())
    entry["used_by"] = email
    _codes_store[code] = entry

    return {
        "status_code": 200,
        "headers": {**_cors_headers(), "Content-Type": "application/json"},
        "body": json.dumps({
            "success": True,
            "message": "Code redeemed successfully",
            "plan": entry.get("plan", "pro"),
            "plan_name": entry.get("plan_name", "专业版"),
        }),
    }
