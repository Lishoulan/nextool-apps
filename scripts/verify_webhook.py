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


def order(order_id, amount="19.00", month=1, status=2, remark=""):
    """按爱发电官方文档 guide.afdian.com/creator/developer 的真实结构构造。

    要点：请求体是 {"ec":200,"em":"ok","data":{"type":"order","order":{...}}}；
    订单号字段是 out_trade_no；status=2 才是交易成功；
    webhook 不带 token（签名只存在于 API 主动查询那条链路）。
    """
    return {
        "ec": 200,
        "em": "ok",
        "data": {
            "type": "order",
            "order": {
                "out_trade_no": order_id,
                "user_id": "adf397fe8374811eaacee52540025c377",
                "user_private_id": "33",
                "plan_id": "a45353328af911eb973052540025c377",
                "month": month,
                "total_amount": amount,
                "show_amount": amount,
                "status": status,
                "remark": remark,
                "product_type": 0,
                "discount": "0.00",
            },
        },
    }


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
    r = hook.handler(FakeRequest(order("order-new", remark="买了月付")))
    b = body_of(r)
    key1 = b.get("key", "")
    check(r["status_code"] == 200 and key1.startswith("NTP-"),
          "付款 → 生成密钥")
    stored = _kv._kv_get(KEY_PREFIX + key1)
    check(isinstance(stored, dict) and stored.get("remark") == "买了月付",
          "密钥已落盘（修复前完全做不到）")
    check(stored and set(stored.keys()) == {"plan", "remark", "created_at", "expires_at"},
          "落盘 4 个字段（remark 取代 email：文档的 webhook 无此字段）")

    # ---- 1b. 响应必须含 ec:200，否则爱发电视为回调失败并反复重试 ----
    check("ec" in b, "响应含 ec 字段（文档硬要求）")
    check(b.get("ec") == 200, "     ec == 200，平台认定回调成功")

    # ---- 2. 该密钥能被 verify 认出 ----
    r = verify.handler(FakeRequest({"key": key1}))
    check(body_of(r).get("valid") is True, "生成的密钥能被 verify 校验通过")

    # ---- 3. 幂等：同一订单回调两次，第二次必须返回同一个密钥 ----
    r2 = hook.handler(FakeRequest(order("order-new", remark="买了月付")))
    b2 = body_of(r2)
    check(b2.get("status") == "already_processed",
          "重复回调 → already_processed（修复前永远为False）")
    check(b2.get("key") == key1, "     返回同一个密钥，不会再发一个")

    # ---- 4. 同一订单回调 5 次，只有 1 个密钥被创建 ----
    keys = set()
    for _ in range(5):
        rr = hook.handler(FakeRequest(order("order-new", remark="买了月付")))
        kk = body_of(rr).get("key", "")
        if kk:
            keys.add(kk)
    check(len(keys) == 1 and keys == {key1},
          "回调 5 次只产生 1 个密钥（实际 %d 个）" % len(keys))

    # 说明：webhook 推送不带 token（签名机制只存在于 API 主动查询那条链路，
    # sign = md5(token + params + ts + user_id)）。所以这里没有验签可测，
    # 准入控制靠 out_trade_no 幂等 + status==2 判定。

    # ---- 6. 非成功状态 → ignored ----
    r = hook.handler(FakeRequest(order("order-new", status=0)))
    check(body_of(r).get("status") == "ignored", "status=0 → ignored")

    # ---- 7. 年付判定 ----
    r = hook.handler(FakeRequest(order("order-year", month=12, amount="199.00")))
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
    r = hook.handler(FakeRequest(# 永久方案：爱发电按 120 个月计
    order("order-expired", month=120, amount="999.00")))
    klife = body_of(r).get("key", "")
    rec = _kv._kv_get(KEY_PREFIX + klife) if klife else None
    check(rec and rec.get("plan") == "lifetime", "plan=lifetime → lifetime")
    check(rec and rec.get("expires_at") is None, "     终身套餐无到期时间")
    _kv._rest("POST", "", ["DEL", ORDER_PREFIX + "order-expired"])
    if klife:
        _kv._rest("POST", "", ["DEL", KEY_PREFIX + klife])

    # ---- 9. 缺 out_trade_no → 400 ----
    bad = order("order-replay")
    bad["data"]["order"]["out_trade_no"] = ""
    r = hook.handler(FakeRequest(bad))
    check(r["status_code"] == 400, "缺 out_trade_no → 400")

    # ---- 10. webhook 无签名可验，准入控制靠幂等 + status==2 ----
    # 文档确认：签名机制只存在于「API 主动查询」那条链路
    # （sign = md5(token + params + ts + user_id)），
    # webhook 推送的请求体里没有 token 或 sign 字段。
    # 因此本handler 不做验签，改为依赖：
    #   1) out_trade_no 幂等（同一订单不会重复发key）
    #   2) status==2 才处理
    # 这两条已在上面逐项验证。

    print()
    print("  %d 项通过, %d 项失败" % (ok_count, fail_count))
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())