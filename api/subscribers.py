"""NextTool 订阅者管理 API

GET  /api/subscribers              返回订阅者统计概览
GET  /api/subscribers?list=true    返回全部订阅者列表

需要 X-Admin-Secret 头进行鉴权（通过 ADMIN_SECRET 环境变量配置）。
"""

import json
import os

SUBSCRIBERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "subscribers.json")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Admin-Secret",
    }


def handler(request):
    # CORS preflight
    if request.method == "OPTIONS":
        return {
            "status_code": 200,
            "headers": _cors_headers(),
            "body": "",
        }

    # 仅允许 GET
    if request.method != "GET":
        return {
            "status_code": 405,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed. Use GET."}),
        }

    # 简单鉴权
    if ADMIN_SECRET:
        secret = ""
        if hasattr(request, "headers"):
            secret = request.headers.get("x-admin-secret", "") or request.headers.get("X-Admin-Secret", "")
        if secret != ADMIN_SECRET:
            return {
                "status_code": 401,
                "headers": {**_cors_headers(), "Content-Type": "application/json"},
                "body": json.dumps({"error": "Unauthorized. Provide X-Admin-Secret header."}),
            }

    # 读取订阅者数据
    subscribers = []
    try:
        if os.path.exists(SUBSCRIBERS_PATH):
            with open(SUBSCRIBERS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    subscribers = data
    except Exception:
        pass

    # 判断是否返回列表
    show_list = False
    if hasattr(request, "args"):
        show_list = request.args.get("list", "").lower() == "true"
    elif hasattr(request, "query"):
        show_list = "list=true" in (request.query or "").lower()

    # 按来源分组统计
    source_stats = {}
    for sub in subscribers:
        source = sub.get("source", "unknown")
        source_stats[source] = source_stats.get(source, 0) + 1

    result = {
        "total": len(subscribers),
        "sources": source_stats,
    }

    if show_list:
        result["subscribers"] = subscribers

    return {
        "status_code": 200,
        "headers": {**_cors_headers(), "Content-Type": "application/json"},
        "body": json.dumps(result, ensure_ascii=False),
    }
