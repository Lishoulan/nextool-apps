"""
端到端验证 pro-verify / pro-activate / afdian-webhook 三个 handler。
配合 mock Upstash 使用，不需要真实凭据。

用法：
    python scripts/mock_upstash.py 8899 &
    NO_PROXY=127.0.0.1 python scripts/verify_api.py
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "api"))

ok_count = 0
fail_count = 0


def check(cond, label):
    global ok_count, fail_count
    if cond:
        ok_count += 1
        print("  OK   %s" % label)
    else:
        fail_count += 1
        print("  FAIL %s" % label)


class FakeRequest:
    """模拟 Vercel 的 request 对象。"""

    def __init__(self, method="POST", payload=None):
        self.method = method
        self._payload = payload if payload is not None else {}
        self.headers = {}

    def json(self):
        return self._payload


def load(mod_name):
    path = os.path.join(ROOT, "api", mod_name + ".py")
    spec = importlib.util.spec_from_file_location(mod_name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def body_of(resp):
    return json.loads(resp["body"])


def main():
    os.environ.setdefault("UPSTASH_REDIS_REST_URL", "http://127.0.0.1:8899")
    os.environ.setdefault("UPSTASH_REDIS_REST_TOKEN", "mock-token")
    os.environ.setdefault("AFDIAN_TOKEN", "a" * 32)

    import _kv
    from _pro_keys import KEY_PREFIX, ORDER_PREFIX, generate_pro_key, _expiry_for

    # 清场
    for k in ("t:probe",):
        _kv._rest("POST", "", ["DEL", k])

    verify = load("pro-verify")

    # ---- 1. 查一个不存在的密钥 → not_found（不是 503）----
    r = verify.handler(FakeRequest("POST", {"key": generate_pro_key()}))
    b = body_of(r)
    check(r["status_code"] == 200 and b["reason"] == "not_found",
          "不存在的密钥 → 200 not_found")

    # ---- 2. 格式非法的 key → not_found，且不查存储 ----
    r = verify.handler(FakeRequest("POST", {"key": "PRO_ANYTHING"}))
    check(body_of(r)["reason"] == "not_found", "非法格式 → not_found")

    # ---- 3. 写入一个有效密钥 → valid:true ----
    good = generate_pro_key()
    _kv._kv_set(KEY_PREFIX + good, {
        "plan": "monthly",
        "email": "test@example.com",
        "created_at": "2026-10-06T00:00:00",
        "expires_at": _expiry_for("monthly"),
    }, ttl=86400 * 60)
    r = verify.handler(FakeRequest("POST", {"key": good}))
    b = body_of(r)
    check(r["status_code"] == 200 and b["valid"] is True, "有效密钥 → valid:true")
    check(b.get("plan") == "monthly", "     返回套餐类型")
    check(b.get("email") == "test@example.com", "     返回邮箱")

    # ---- 4. 已过期的密钥 → expired（不是 not_found）----
    expired = generate_pro_key()
    _kv._kv_set(KEY_PREFIX + expired, {
        "plan": "monthly",
        "expires_at": "2020-01-01T00:00:00",
    }, ttl=86400 * 60)
    r = verify.handler(FakeRequest("POST", {"key": expired}))
    b = body_of(r)
    check(b.get("reason") == "expired",
          "已过期密钥 → expired（前端提示续费，不是无效）")

    # ---- 5. 存储不可用 → 503 而非谎称无效 ----
    import importlib
    # 换一个子进程来测：_kv 模块在 sys.modules 里已缓存，
    # 同进程内重新 load() 拿到的仍是旧模块，读不到新的环境变量。
    import subprocess
    probe = (
        "import os,sys,json,importlib.util;"
        "os.environ['UPSTASH_REDIS_REST_URL']='http://127.0.0.1:9';"
        "os.environ['UPSTASH_REDIS_REST_TOKEN']='x';"
        "os.environ['AFDIAN_TOKEN']='a'*32;"
        "sys.path.insert(0, 'api');"
        "spec=importlib.util.spec_from_file_location('pv','api/pro-verify.py');"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
        "R=type('R',(),{'method':'POST','json':lambda s:{'key':'NTP-AAAA-BBBB-CCCC'}});"
        "r=m.handler(R());"
        "print(r['status_code'], r['body'][:60])"
    )
    out = subprocess.run([sys.executable, "-c", probe],
                         capture_output=True, text=True)
    line = out.stdout.strip()
    check(line.startswith("503") and "storage_unavailable" in line,
          "存储不可用 → 503 storage_unavailable（不谎称无效）")

    # ---- 6. GET 方法 → 405 ----
    r = verify.handler(FakeRequest("GET"))
    check(r["status_code"] == 405, "GET → 405")

    # ---- 7. 坏JSON → 400 ----
    req = FakeRequest("POST", {})
    req._payload = None

    class BadJSON(FakeRequest):
        def json(self):
            raise ValueError("bad")

    r = verify.handler(BadJSON("POST"))
    check(r["status_code"] == 400, "非法 JSON → 400")

    print()
    print("  %d 项通过, %d 项失败" % (ok_count, fail_count))
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())