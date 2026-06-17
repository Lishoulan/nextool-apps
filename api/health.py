"""NexTool API Proxy - Health Check Endpoint"""

import json


def handler(request):
    return {
        "status_code": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "status": "ok",
            "service": "NexTool API Proxy",
            "version": "1.0.0",
        }),
    }
