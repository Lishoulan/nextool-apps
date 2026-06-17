"""
NexTool API Proxy - Afdian Webhook
爱发电付款回调 → 自动生成 Pro 密钥
Vercel Serverless Function
"""

import os
import json
import secrets
from datetime import datetime, timedelta

PRO_KEYS_JSON = os.environ.get("PRO_KEYS_JSON", '{"keys":{},"orders":{}}')
AFDIAN_TOKEN = os.environ.get("AFDIAN_TOKEN", "")


def _load_pro_keys():
    try:
        return json.loads(PRO_KEYS_JSON)
    except (json.JSONDecodeError, TypeError):
        return {"keys": {}, "orders": {}}


def _generate_pro_key():
    parts = [secrets.token_hex(2).upper() for _ in range(3)]
    return f"NTP-{parts[0]}-{parts[1]}-{parts[2]}"


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

    # Verify Afdian token
    if AFDIAN_TOKEN:
        received_token = body.get("token", "")
        if received_token != AFDIAN_TOKEN:
            return {
                "status_code": 403,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid Afdian token"}),
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

    # Check if already processed
    data = _load_pro_keys()
    if order_id in data.get("orders", {}):
        existing_key = data["orders"][order_id].get("key", "")
        return {
            "status_code": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps({"status": "already_processed", "key": existing_key}),
        }

    # Determine plan duration
    if "year" in str(order.get("plan", "")).lower() or float(amount) >= 100:
        plan = "yearly"
        duration_days = 365
    elif "lifetime" in str(order.get("plan", "")).lower():
        plan = "lifetime"
        duration_days = 0
    else:
        plan = "monthly"
        duration_days = 30

    # Generate Pro key
    key = _generate_pro_key()
    expires_at = None if plan == "lifetime" else (datetime.now() + timedelta(days=duration_days)).isoformat()

    data["keys"][key] = {
        "plan": plan,
        "email": email,
        "note": f"Afdian order: {order_id}",
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "source": "afdian",
        "afdian_user_id": user_id,
        "afdian_order_id": order_id,
        "amount": amount,
    }
    data["orders"][order_id] = {
        "key": key,
        "plan": plan,
        "email": email,
        "amount": amount,
        "created_at": datetime.now().isoformat(),
    }

    # Note: In Vercel serverless, we can't persist to file.
    # The PRO_KEYS_JSON env var is read-only.
    # For production, use Vercel KV, Upstash Redis, or a database.
    # For now, return the key and log it.

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
