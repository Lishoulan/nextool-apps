"""
NexTool Pro 密钥存储层 —— Upstash Redis REST 封装。

设计要点
--------
1. 环境变量缺失时**导入即抛错**，不静默回退到内存或空表。
   静默回退会产生「webhook 返回 200 但密钥从未落盘」这种看起来在
   工作、实际什么都没发生的故障，比直接报错危险得多。

2. 只用标准库 urllib。本模块在冷启动路径上，少一个依赖少一个故障点
   （requirements.txt 只有 httpx，这里不必依赖它）。

3. 所有错误统一抛 KVError，由调用方决定降级策略——因为「密钥不存在」
   与「存储不可用」必须区分：前者返回 not_found，后者返回 503。
"""

import json
import os
import urllib.error
import urllib.request
from urllib.parse import quote

_UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL", "").rstrip("/")
_UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")

if not _UPSTASH_URL or not _UPSTASH_TOKEN:
    _missing = [
        name
        for name, val in (
            ("UPSTASH_REDIS_REST_URL", _UPSTASH_URL),
            ("UPSTASH_REDIS_REST_TOKEN", _UPSTASH_TOKEN),
        )
        if not val
    ]
    raise RuntimeError(
        "Upstash 未配置，缺少环境变量: " + ", ".join(_missing) + "。"
        "Pro 密钥存储不可用——本服务拒绝在无持久化的情况下启动，"
        "否则 webhook 会返回 200 但密钥从未落盘。"
    )

_TIMEOUT_S = float(os.environ.get("UPSTASH_TIMEOUT_S", "3"))


class KVError(RuntimeError):
    """存储层访问失败。与「密钥不存在」这类业务结果区分开。"""


def _rest(method, path, payload=None):
    """调用一次 Upstash REST 接口，返回解析后的 result 字段。"""
    url = _UPSTASH_URL + path
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + _UPSTASH_TOKEN)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read()[:200].decode("utf-8", "replace")
        except Exception:
            pass
        raise KVError("Upstash HTTP %s: %s" % (exc.code, detail)) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise KVError("Upstash 网络错误: %s" % exc) from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KVError("Upstash 返回非 JSON: %r" % raw[:200]) from exc

    if isinstance(parsed, dict):
        if parsed.get("error"):
            raise KVError("Upstash 返回错误: %s" % parsed["error"])
        return parsed.get("result")
    return parsed


def _kv_get(key):
    """读一个 key。不存在返回 None（这是正常路径，不是错误）。"""
    result = _rest("GET", "/get/" + quote(key, safe=""))
    if result is None:
        return None
    if isinstance(result, (bytes, bytearray)):
        result = result.decode("utf-8")
    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError as exc:
            raise KVError("key %r 的值不是合法 JSON: %s" % (key, exc)) from exc
    return result


def _kv_set(key, value, ttl=None):
    """写一个 key，可选 TTL（秒）。"""
    cmd = ["SET", key, json.dumps(value, ensure_ascii=False)]
    if ttl is not None:
        cmd += ["EX", str(int(ttl))]
    return _rest("POST", "", cmd) == "OK"


def _kv_set_nx(key, value, ttl=None):
    """SET ... NX：只在 key 不存在时写入。

    返回 True 表示本次写入抢到，False 表示已存在。
    Redis 单线程串行执行 SET，因此两个并发请求必然只有一个抢到——
    这就是订单幂等所需的全部机制，不需要 WATCH/MULTI、Lua 或分布式锁。
    """
    cmd = ["SET", key, json.dumps(value, ensure_ascii=False), "NX"]
    if ttl is not None:
        cmd += ["EX", str(int(ttl))]
    return _rest("POST", "", cmd) == "OK"


def _kv_ttl(key):
    """剩余 TTL 秒数；-1 表示无过期，-2 表示key 不存在。"""
    result = _rest("POST", "", ["TTL", key])
    return int(result) if result is not None else -2