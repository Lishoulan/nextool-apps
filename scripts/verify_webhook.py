"""
afdian-webhook 端到端验证：证明幂等从「从未生效」变成「真正生效」。

用法：
    python scripts/mock_upstash.py 8899 &
    NO_PROXY=127.0.0.1 AFDIAN_TOKEN=<32位token> python scripts/verify_webhook.py
"""
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "api"))

TOKEN = os.environ.get("AFDIAN_TOKEN", "t" * 32)

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
    def __init__(self, payload, method="POST"):
        self.method = method
        self._payload = payload
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


def order(order_id, amount="19", plan="monthly", email="buyer@example.com",
          status=1, ts=None):
    payload = {
        "token": TOKEN,
        "order": {
            "order_id": order_id,
            "user_id": "u123",
            "email": email,
            "total_amount": amount,
            "plan": plan,
            "status": status,
        },
    }
    if ts is not None:
        payload["timestamp"] = ts
    return payload


def main():
    os.environ.setdefault("UPSTASH_REDIS_REST_URL", "http://127.0.0.1:8899")
    os.environ.setdefault("UPSTASH_REDIS_REST_TOKEN", "mock-token")
    os.environ["AFDIAN_TOKEN"] = TOKEN

    import _kv
    from _pro_keys import KEY_PREFIX, ORDER_PREFIX

    hook = load("afdian-webhook")
    verify = load("pro-verify")

    # 清场
    for oid in ("order-dup", "order-new", "order-expired",
                "order-year", "order-wrongtoken", "order-replay"):
        _kv._rest("POST", "", ["DEL", ORDER_PREFIX + oid])

    # ---- 1. 付款 → 生成密钥且真的落盘 ----
    r = hook.handler(FakeRequest(order("order-new", email="new@example.com")))
    b = body_of(r)
    key1 = b.get("key", "")
    check(r["status_code"] == 200 and key1.startswith("NTP-"),
          "付款 → 生成密钥")
    stored = _kv._kv_get(KEY_PREFIX + key1)
    check(isinstance(stored, dict) and stored.get("email") == "new@example.com",
          "密钥已落盘（这是修复前完全做不到的）")
    check(stored and set(stored.keys()) == {"plan", "email", "created_at", "expires_at"},
          "密钥只保留读取方用得到的 4 个字段")

    # ---- 2. 该密钥能被 verify 认出 ----
    r = verify.handler(FakeRequest({"key": key1}))
    check(body_of(r).get("valid") is True, "生成的密钥能被 verify 校验通过")

    # ---- 3. 幂等：同一订单回调两次，第二次必须返回同一个密钥 ----
    r2 = hook.handler(FakeRequest(order("order-new", email="new@example.com")))
    b2 = body_of(r2)
    check(b2.get("status") == "already_processed",
          "重复回调 → already_processed（修复前永远为False）")
    check(b2.get("key") == key1, "     返回同一个密钥，不会再发一个")

    # ---- 4. 同一订单回调 5 次，只有 1 个密钥被创建 ----
    keys = set()
    for _ in range(5):
        rr = hook.handler(FakeRequest(order("order-new", email="new@example.com")))
        kk = body_of(rr).get("key", "")
        if kk:
            keys.add(kk)
    check(len(keys) == 1 and keys == {key1},
          "回调 5 次只产生 1 个密钥（实际 %d 个）" % len(keys))

    # ---- 5. 错误 token → 403 ----
    bad = order("order-wrongtoken")
    bad["token"] = "wrong-token-value-x"
    r = hook.handler(FakeRequest(bad))
    check(r["status_code"] == 403, "错误 token → 403")

    # ---- 6. 非成功状态 → ignored ----
    r = hook.handler(FakeRequest(order("order-new", status=0)))
    check(body_of(r).get("status") == "ignored", "status=0 → ignored")

    # ---- 7. 年付判定 ----
    r = hook.handler(FakeRequest(order("order-year", amount="199")))
    ky = body_of(r).get("key", "")
    rec = _kv._kv_get(KEY_PREFIX + ky) if ky else None
    check(rec and rec.get("plan") == "yearly",
          "amount>=100 → yearly")
    _kv._rest("POST", "", ["DEL", ORDER_PREFIX + "order-year"])
    if ky:
        _kv._rest("POST", "", ["DEL", KEY_PREFIX + ky])

    # ---- 8. 终身套餐 ----
    # lifetime 走的是 elif 分支，金额必须小于 100 —— 原代码的判定顺序
    # 是先year（含 amount>=100）再 lifetime，保持不变。
    r = hook.handler(FakeRequest(order("order-expired", plan="lifetime",
                                       amount="49")))
    klife = body_of(r).get("key", "")
    rec = _kv._kv_get(KEY_PREFIX + klife) if klife else None
    check(rec and rec.get("plan") == "lifetime", "plan=lifetime → lifetime")
    check(rec and rec.get("expires_at") is None, "     终身套餐无到期时间")
    _kv._rest("POST", "", ["DEL", ORDER_PREFIX + "order-expired"])
    if klife:
        _kv._rest("POST", "", ["DEL", KEY_PREFIX + klife])

    # ---- 9. 防重放：过期的 timestamp → 403 ----
    r = hook.handler(FakeRequest(order("order-replay",
                                       ts=int(time.time()) - 600)))
    check(r["status_code"] == 403, "timestamp 超 5 分钟 → 403（防重放）")
    _kv._rest("POST", "", ["DEL", ORDER_PREFIX + "order-replay"])

    # ---- 10. AFDIAN_TOKEN 未配置 → 503（fail-closed）----
    import subprocess
    probe = (
        "import os,sys,importlib.util,json;"
        "os.environ.pop('AFDIAN_TOKEN',None);"
        "os.environ['UPSTASH_REDIS_REST_URL']='http://127.0.0.1:8899';"
        "os.environ['UPSTASH_REDIS_REST_TOKEN']='mock';"
        "sys.path.insert(0,'api');"
        "spec=importlib.util.spec_from_file_location('aw','api/afdian-webhook.py');"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
        "R=type('R',(),{'method':'POST','json':lambda s:{'order':{}}});"
        "r=m.handler(R());print(r['status_code'])"
    )
    out = subprocess.run([sys.executable, "-c", probe],
                         capture_output=True, text=True)
    check(out.stdout.strip().startswith("503"),
          "AFDIAN_TOKEN 未配置 → 503（fail-closed，修复前是放行）")

    # ---- 11. 弱 token 启动即拒绝 ----
    probe2 = (
        "import os,sys,importlib.util;"
        "os.environ['AFDIAN_TOKEN']='short';"
        "os.environ['UPSTASH_REDIS_REST_URL']='http://127.0.0.1:8899';"
        "os.environ['UPSTASH_REDIS_REST_TOKEN']='mock';"
        "sys.path.insert(0,'api');"
        "spec=importlib.util.spec_from_file_location('aw','api/afdian-webhook.py');"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)"
    )
    out2 = subprocess.run([sys.executable, "-c", probe2],
                          capture_output=True, text=True)
    check("16" in out2.stderr and "AFDIAN_TOKEN" in out2.stderr,
          "弱 AFDIAN_TOKEN → 启动即 RuntimeError")

    print()
    print("  %d 项通过, %d 项失败" % (ok_count, fail_count))
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())