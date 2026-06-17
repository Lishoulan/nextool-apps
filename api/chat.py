"""
NexTool API Proxy - Vercel Serverless Function
Proxies chat completions to DeepSeek API with rate limiting.
"""

import os
import time
import json
import httpx
from datetime import datetime

LLM_API_KEY = os.environ.get("DEEPSEEK_API_KEY", os.environ.get("LLM_API_KEY", ""))
LLM_API_URL = os.environ.get("LLM_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
RATE_LIMIT_PER_HOUR = 10

# In-memory rate limiting (resets on cold start)
ip_usage: dict = {}


def get_client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    forwarded = request.headers.get("x-real-ip")
    if forwarded:
        return forwarded.strip()
    return "unknown"


def check_rate_limit(ip: str) -> tuple:
    now = time.time()
    one_hour_ago = now - 3600

    if ip not in ip_usage:
        ip_usage[ip] = []

    ip_usage[ip] = [t for t in ip_usage[ip] if t > one_hour_ago]

    remaining = max(0, RATE_LIMIT_PER_HOUR - len(ip_usage[ip]))
    return len(ip_usage[ip]) < RATE_LIMIT_PER_HOUR, remaining


def record_usage(ip: str):
    if ip not in ip_usage:
        ip_usage[ip] = []
    ip_usage[ip].append(time.time())


def handler(request):
    """Vercel Python serverless function handler."""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return {
            "status_code": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "86400",
            },
            "body": "",
        }

    # Only allow POST
    if request.method != "POST":
        return {
            "status_code": 405,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Method not allowed. Use POST."}),
        }

    # Parse body
    try:
        body = request.json() if hasattr(request, "json") else json.loads(request.body or "{}")
    except Exception:
        return {
            "status_code": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    client_ip = get_client_ip(request)

    # Check if user provided their own API key (bypasses rate limit)
    user_api_key = body.pop("api_key", None)
    api_key = user_api_key or LLM_API_KEY

    # If using proxy key (no user key), enforce rate limit
    if not user_api_key:
        allowed, remaining = check_rate_limit(client_ip)
        if not allowed:
            return {
                "status_code": 429,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "X-RateLimit-Limit": str(RATE_LIMIT_PER_HOUR),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Window": "1h",
                },
                "body": json.dumps({
                    "error": {
                        "message": "Rate limit exceeded. 10 requests per hour for free users.",
                        "limit": RATE_LIMIT_PER_HOUR,
                        "remaining": 0,
                        "window": "1h",
                    }
                }),
            }

    # Build headers for DeepSeek
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Forward request to DeepSeek (synchronous in Vercel Python runtime)
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                LLM_API_URL,
                json=body,
                headers=headers,
            )
    except httpx.TimeoutException:
        return {
            "status_code": 504,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": {"message": "DeepSeek API timeout"}}),
        }
    except httpx.ConnectError:
        return {
            "status_code": 502,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": {"message": "Cannot connect to DeepSeek API"}}),
        }
    except Exception as e:
        return {
            "status_code": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": {"message": str(e)}}),
        }

    # Record usage after successful request (only for proxy key)
    if not user_api_key:
        record_usage(client_ip)

    # Return response
    response_headers = {"Access-Control-Allow-Origin": "*"}
    try:
        resp_data = response.json()
    except Exception:
        return {
            "status_code": 502,
            "headers": response_headers,
            "body": json.dumps({"error": {"message": "Invalid response from DeepSeek"}}),
        }

    return {
        "status_code": response.status_code,
        "headers": {**response_headers, "Content-Type": "application/json"},
        "body": json.dumps(resp_data),
    }
