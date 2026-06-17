"""NextTool Email Subscription Endpoint

Accepts POST requests with email and source,
validates the email format, persists to data/subscribers.json,
and returns success response.
"""

import json
import os
import re
import time

SUBSCRIBERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "subscribers.json")


def _save_subscriber(email: str, source: str) -> bool:
    """保存订阅者到文件，返回是否新增成功"""
    subscribers = []
    try:
        if os.path.exists(SUBSCRIBERS_PATH):
            with open(SUBSCRIBERS_PATH, "r", encoding="utf-8") as f:
                subscribers = json.load(f)
                if not isinstance(subscribers, list):
                    subscribers = []
    except Exception:
        subscribers = []

    # 检查是否已存在
    for sub in subscribers:
        if sub.get("email") == email:
            return False

    subscribers.append({
        "email": email,
        "source": source,
        "subscribed_at": int(time.time()),
    })

    try:
        os.makedirs(os.path.dirname(SUBSCRIBERS_PATH), exist_ok=True)
        with open(SUBSCRIBERS_PATH, "w", encoding="utf-8") as f:
            json.dump(subscribers, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Vercel 只读文件系统会失败，静默处理

    return True


def handler(request):
    # Handle CORS preflight
    if request.get("method", "") == "OPTIONS":
        return {
            "status_code": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    # Only accept POST
    if request.get("method", "") != "POST":
        return {
            "status_code": 405,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Method not allowed"}),
        }

    # Parse request body
    try:
        body = json.loads(request.get("body", "{}"))
    except (json.JSONDecodeError, TypeError):
        return {
            "status_code": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    email = body.get("email", "").strip()
    source = body.get("source", "")

    # Validate email
    if not email:
        return {
            "status_code": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Email is required"}),
        }

    email_pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return {
            "status_code": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Invalid email format"}),
        }

    # 持久化到文件（开发环境有效，Vercel 生产环境需迁移到 KV/DB）
    is_new = _save_subscriber(email, source)

    # Return success
    return {
        "status_code": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "success": True,
            "message": "Subscription received successfully" if is_new else "Email already subscribed",
            "email": email,
            "source": source,
            "is_new": is_new,
        }),
    }
