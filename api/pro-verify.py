"""
NexTool API Proxy - Pro Key Verification
Vercel Serverless Function
"""

import os
import json
import secrets
from datetime import datetime, timedelta

# Pro keys stored in Vercel KV or environment variable
# For simplicity, we use a JSON string in environment variable
PRO_KEYS_JSON = os.environ.get("PRO_KEYS_JSON", '{"keys":{},"orders":{}}')
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "nextool-admin-2026")
AFDIAN_TOKEN = os.environ.get("AFDIAN_TOKEN", "")


def _load_pro_keys():
    try:
        return json.loads(PRO_KEYS_JSON)
    except (json.JSONDecodeError, TypeError):
        return {"keys": {}, "orders": {}}


def _generate_pro_key():
    parts = [secrets.token_hex(2).upper() for _ in range(3)]
    return f"NTP-{parts[0]}-{parts[1]}-{parts[2]}"


def _is_pro_key_valid(key, data):
    if not key or not key.startswith("NTP-"):
        return False, None
    key_info = data["keys"].get(key)
    if not key_info:
        return False, None
    if key_info.get("expires_at"):
        expires = datetime.fromisoformat(key_info["expires_at"])
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
    data = _load_pro_keys()
    valid, key_info = _is_pro_key_valid(key, data)

    if valid and key_info:
        return {
            "status_code": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps({
                "valid": True,
                "plan": key_info.get("plan", "monthly"),
                "expires_at": key_info.get("expires_at"),
                "email": key_info.get("email", ""),
            }),
        }
    elif key_info and key_info.get("expires_at"):
        return {
            "status_code": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps({
                "valid": False,
                "reason": "expired",
                "expired_at": key_info["expires_at"],
                "plan": key_info.get("plan", "monthly"),
            }),
        }

    return {
        "status_code": 200,
        "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
        "body": json.dumps({"valid": False, "reason": "not_found"}),
    }
