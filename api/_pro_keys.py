"""
Pro 密钥的公共逻辑：格式校验、过期判断、TTL 计算。

原先 pro-verify.py 与 pro-activate.py 各自持有一份逐字符相同的
_load_pro_keys() 与 _is_pro_key_valid()，改动时极易漏改一处，
因此抽到本模块，三个 API 统一复用。
"""

from datetime import datetime, timedelta

KEY_PREFIX = "nextool:pro:key:"
ORDER_PREFIX = "nextool:pro:order:"

# 订单记录保留 10 年：密钥可能早已过期，但退款、对账、排障
# 都要回查「当初是不是付过钱、付了多少」。
ORDER_TTL_SECONDS = 10 * 365 * 24 * 3600


def _looks_like_key(key):
    """密钥格式：NTP-XXXX-XXXX-XXXX（十六进制分组）。"""
    if not key or not isinstance(key, str):
        return False
    if not key.startswith("NTP-"):
        return False
    parts = key.split("-")
    if len(parts) != 4:
        return False
    return all(len(p) == 4 for p in parts[1:])


def _key_ttl_seconds(expires_at_iso):
    """密钥记录的 TTL：到期之后再留 30 天宽限。

    留宽限的原因：校验接口需要能读出 expires_at，才能区分
    「密钥已过期」（提示续费）和「密钥无效」（提示联系客服）。
    Redis key 一旦过期就什么都读不到，文案会退化成「无效」，
    让续费用户以为自己被删号了。

    真正的到期判定仍在应用层，Redis 的过期只负责回收空间。
    两层职责分开：Redis 管「数据还在不在」，应用管「还有效吗」。
    """
    grace = 30 * 24 * 3600
    long_lived = 10 * 365 * 24 * 3600
    if not expires_at_iso:
        return long_lived
    try:
        expires = datetime.fromisoformat(expires_at_iso)
    except (TypeError, ValueError):
        # 存量数据里格式异常，按长期保留处理，不在这里丢弃记录
        return long_lived
    remaining = (expires - datetime.now()).total_seconds()
    return int(max(remaining, 0) + grace)


def _plan_duration_days(plan):
    """套餐名 → 有效天数。终身套餐返回 None（不过期）。"""
    if plan == "lifetime":
        return None
    if plan == "yearly":
        return 365
    return 30


def _expiry_for(plan):
    """按套餐算出ISO 格式的到期时间；终身套餐返回 None。"""
    days = _plan_duration_days(plan)
    if days is None:
        return None
    return (datetime.now() + timedelta(days=days)).isoformat()


def generate_pro_key():
    """生成一个新的 Pro 密钥。"""
    import secrets
    return "NTP-%s-%s-%s" % (
        secrets.token_hex(2).upper(),
        secrets.token_hex(2).upper(),
        secrets.token_hex(2).upper(),
    )