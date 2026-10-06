"""
_kv.py 的验证脚本，配合 scripts/mock_upstash.py 使用。

启动 mock：
    python scripts/mock_upstash.py 8899 &
然后：
    python scripts/verify_kv.py
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

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


def main():
    os.environ.setdefault("UPSTASH_REDIS_REST_URL", "http://127.0.0.1:8899")
    os.environ.setdefault("UPSTASH_REDIS_REST_TOKEN", "mock-token")

    import _kv

    # mock 的状态跨进程运行保留，所以先清掉本脚本会用到的 key，
    # 否则第二次跑时 t:never-written 已经存在，SET NX 必然返回 False。
    for k in ("t:1", "t:missing", "t:ttl", "t:ttl2", "t:不存在",
              "t:idem", "t:fresh", "t:fresh2", "t:never-written",
              "t:race", "t:broken", "t:broken2"):
        _kv._rest("POST", "", ["DEL", k])

    # 1. 读写往返（含中文与嵌套结构）
    payload = {"plan": "monthly", "expires_at": "2099-01-01T00:00:00",
               "email": "用户@例子.com"}
    _kv._kv_set("t:1", payload)
    check(_kv._kv_get("t:1") == payload, "读写往返（含中文）")

    # 2. 读不存在的 key 返回 None，不是异常
    check(_kv._kv_get("t:missing") is None, "读不存在的 key → None")

    # 3. TTL 生效
    _kv._kv_set("t:ttl", {"x": 1}, ttl=1)
    check(_kv._kv_get("t:ttl") is not None, "TTL 内可读")
    time.sleep(1.6)
    check(_kv._kv_get("t:ttl") is None, "TTL 过期后读不到")

    # 4. _kv_ttl
    _kv._kv_set("t:ttl2", {"x": 1}, ttl=100)
    ttl = _kv._kv_ttl("t:ttl2")
    check(90 <= ttl <= 100, "TTL 查询返回约设��值 (实际 %s)" % ttl)
    check(_kv._kv_ttl("t:不存在") == -2, "TTL 查询不存在的 key → -2")

    # 5. SET NX 连续两次：第一次抢到，第二次失败
    _kv._kv_set("t:idem", {"key": "OLD"})
    first = _kv._kv_set_nx("t:idem", {"key": "NEW"})
    check(first is False, "SET NX 对已存在的 key 返回 False")
    _kv._kv_set("t:fresh", {"k": 1})
    del_first = None
    _kv._kv_set("t:fresh2", {"k": 1})
    del_first = _kv._kv_set_nx("t:fresh2", {"k": 2})
    check(del_first is False, "SET NX 对刚写的 key 再次调用 → False")
    brand_new = _kv._kv_set_nx("t:never-written", {"k": 1})
    check(brand_new is True, "SET NX 对全新 key → True")

    # 6. 并发：10 线程同时 SET NX 同一 key，恰好 1 个成功
    winners = []
    lock = threading.Lock()
    start = threading.Barrier(10)

    def race(i):
        start.wait()  # 让所有线程尽量同时发起
        got = _kv._kv_set_nx("t:race", {"worker": i})
        with lock:
            winners.append(got)

    threads = [threading.Thread(target=race, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    true_count = sum(1 for w in winners if w)
    check(true_count == 1,
          "10 线程并发 SET NX 同一 key → 恰好 1 个成功 (实际 %d)" % true_count)
    # 留下的值必须是某个自称写成功的那个线程的值——不能是另一个
    # 没抢到的线程把先前赢家覆盖了（那才说明 NX 失效）。
    stored_worker = _kv._kv_get("t:race")["worker"]
    check(0 <= stored_worker < 10,
          "并发写留下的值来自某个线程 (worker=%s)" % stored_worker)

    # 7. 非法 JSON 值 → 抛 KVError
    import json as _json
    import urllib.request
    req = urllib.request.Request(
        os.environ["UPSTASH_REDIS_REST_URL"] + "/set-broken",
        data=_json.dumps(["SET", "t:broken", "not-json-at-all"]).encode(),
        method="POST")
    req.add_header("Authorization", "Bearer mock-token")
    try:
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass
    # 直接塞一个非法 JSON 字符串
    req2 = urllib.request.Request(
        os.environ["UPSTASH_REDIS_REST_URL"],
        data=_json.dumps(["SET", "t:broken2", "{oops"]).encode(),
        method="POST")
    req2.add_header("Authorization", "Bearer mock-token")
    urllib.request.urlopen(req2, timeout=3)
    try:
        _kv._kv_get("t:broken2")
        check(False, "非法 JSON 值应抛 KVError")
    except _kv.KVError:
        check(True, "非法 JSON 值→ 抛 KVError")
    except Exception as exc:
        check(False, "非法 JSON 值应抛 KVError（实际抛了 %s）" % type(exc).__name__)

    # 8. 存储不可用时抛 KVError，而不是静默返回 None。
    # 用一个真实的不可达地址验证——最容易被写错的地方就是这里：
    # 静默返回 None 会被上层当成「密钥不存在」，把存储故障
    # 伪装成业务结果。
    saved_url = os.environ["UPSTASH_REDIS_REST_URL"]
    os.environ["UPSTASH_REDIS_REST_URL"] = "http://127.0.0.1:9"
    try:
        import importlib
        importlib.reload(_kv)
        try:
            _kv._kv_get("t:任何")
            check(False, "连不上存储时应抛 KVError 而非返回 None")
        except _kv.KVError:
            check(True, "连不上存储 → 抛 KVError（不静默返回 None）")
        except Exception as exc:
            check(False, "连不上存储 → 抛 KVError（实际 %s）"
                  % type(exc).__name__)
    finally:
        os.environ["UPSTASH_REDIS_REST_URL"] = saved_url
        import importlib
        importlib.reload(_kv)

    print()
    print("  %d 项通过, %d 项失败" % (ok_count, fail_count))
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())