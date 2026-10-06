"""
本地 mock Upstash Redis，用于在没有真实凭据时验证 _kv.py 的读写逻辑。

用法：
    python scripts/mock_upstash.py 8899 &
    UPSTASH_REDIS_REST_URL=http://127.0.0.1:8899 \
    UPSTASH_REDIS_REST_TOKEN=mock \
    python -c "..."

只实现 _kv.py 用到的四条命令：GET / SET（含 NX、EX）/ TTL。
"""

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

STORE = {}
EXPIRES = {}


def _purge_if_expired(key):
    if key in EXPIRES and EXPIRES[key] < time.time():
        STORE.pop(key, None)
        EXPIRES.pop(key, None)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/get/"):
            key = unquote(self.path[len("/get/"):])
            _purge_if_expired(key)
            self._send({"result": STORE.get(key)})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            cmd = json.loads(self.rfile.read(length) or b"[]")
        except Exception as exc:
            self._send({"error": "bad request: %r" % exc})
            return

        if not cmd:
            self._send({"error": "empty command"})
            return

        op = str(cmd[0]).upper()

        if op == "SET":
            key, value = cmd[1], cmd[2]
            _purge_if_expired(key)
            if "NX" in cmd and key in STORE:
                # SET NX 在 key 已存在时返回 nil
                self._send({"result": None})
                return
            STORE[key] = value
            if "EX" in cmd:
                EXPIRES[key] = time.time() + int(cmd[cmd.index("EX") + 1])
            else:
                EXPIRES.pop(key, None)
            self._send({"result": "OK"})
            return

        if op == "GET":
            key = cmd[1]
            _purge_if_expired(key)
            self._send({"result": STORE.get(key)})
            return

        if op == "DEL":
            removed = 0
            for k in cmd[1:]:
                if k in STORE:
                    del STORE[k]
                    removed += 1
                EXPIRES.pop(k, None)
            self._send({"result": removed})
            return

        if op == "TTL":
            key = cmd[1]
            _purge_if_expired(key)
            if key not in STORE:
                self._send({"result": -2})
            elif key not in EXPIRES:
                self._send({"result": -1})
            else:
                self._send({"result": int(EXPIRES[key] - time.time())})
            return

        self._send({"error": "unsupported command: %s" % op})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    print("mock upstash listening on http://127.0.0.1:%d" % port, flush=True)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()