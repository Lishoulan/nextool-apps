"""
手工发放 Pro 密钥 —— 方案 A（不依赖 webhook）。

用途
----
爱发电的 webhook 推送不带签名，无法验明来源，所以本项目改用
「人工发放」：小蓝在爱发电后台看到付款，用这个脚本生成密钥并发给用户。

为什么需要脚本而不是手写
------------------------
密钥必须写进 Redis 才能被 /api/pro/verify 认出来。手工构造 JSON
容易漏字段或写错前缀，而 /api/pro/verify 认不出来时只会回not_found，
用户只会看到「密钥无效」——排查起来很费时间。

幂等
----
同一个订单号重复执行不会产生第二个密钥，而是把原密钥打印出来。
这很关键：万一邮件发失败需要重发，或者你不确定上次有没有发成功。

用法
----
    # 环境变量（建议写进 ~/.bashrc 或用 .env，不要提交进仓库）
    export UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
    export UPSTASH_REDIS_REST_TOKEN=xxxxxxxx

    # 1) 预览：不写库，只打印将要发生什么（默认行为，安全）
    python scripts/issue_key.py --order 2026100622001 --plan monthly

    # 2) 确认无误后真正写入
    python scripts/issue_key.py --order 2026100622001 --plan monthly --commit

    # 3) 查某个订单是否已发过
    python scripts/issue_key.py --order 2026100622001 --check

    # 4) 列出最近的密钥（对账用）
    python scripts/issue_key.py --list

    # 5) 作废某个密钥（用户退款/误发）
    python scripts/issue_key.py --order 2026100622001 --revoke --commit
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

PLANS = ("monthly", "yearly", "lifetime")


def human_ttl(expires_at):
    if not expires_at:
        return "永久"
    try:
        d = datetime.fromisoformat(expires_at)
    except (TypeError, ValueError):
        return "未知"
    return (d.strftime("%Y-%m-%d") + f"（{(d - datetime.now()).days} 天后）")


def main():
    ap = argparse.ArgumentParser(
        description="手工发放 Pro 密钥（方案 A：不依赖 webhook）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--order", help="爱发电订单号 out_trade_no")
    ap.add_argument("--plan", choices=PLANS, default="monthly", help="套餐，默认 monthly")
    ap.add_argument("--amount", default="", help="订单金额，仅记录用")
    ap.add_argument("--note", default="", help="备注，会存进密钥记录便于日后对账")
    ap.add_argument("--commit", action="store_true",
                    help="真正写入。不加此参数只做预览（推荐先预览）")
    ap.add_argument("--check", action="store_true",
                    help="只查该订单是否已发过密钥")
    ap.add_argument("--revoke", action="store_true",
                    help="作废该订单的密钥")
    ap.add_argument("--list", action="store_true", help="列出全部密钥记录")
    args = ap.parse_args()

    # 环境变量缺失时 _kv会在 import 阶段直接抛错，这比在这里检查更好：
    # 它保证「静默降级」不可能发生。
    try:
        import _kv
        from _pro_keys import (KEY_PREFIX, ORDER_PREFIX, ORDER_TTL_SECONDS,
                               generate_pro_key, _expiry_for, _plan_duration_days,
                               _key_ttl_seconds)
    except RuntimeError as exc:
        print("无法连接密钥存储：\n  %s\n" % exc)
        print("请先设置这两个环境变量：")
        print("  UPSTASH_REDIS_REST_URL")
        print("  UPSTASH_REDIS_REST_TOKEN")
        return 2

    # ---- 列出全部 ----
    if args.list:
        print("正在扫描 %s* …" % KEY_PREFIX)
        print("Upstash 免费版不提供 SCAN 全库遍历，"
              "所以这里需要你提供具体的订单号或密钥。")
        print("提示：爱发电后台能看到订单号，用 --order 逐个查更实际。")
        return 0

    if not args.order:
        ap.print_help()
        return 1

    order_id = args.order.strip()
    order_key = ORDER_PREFIX + order_id

    # ---- 查询 ----
    if args.check:
        rec = _kv._kv_get(order_key)
        if not rec:
            print("订单 %s 尚未发放密钥。" % order_id)
            return 0
        key = rec.get("key", "")
        print("订单 %s 已发放密钥。" % order_id)
        print("  密钥      : %s" % (key or "(空)"))
        print("  套餐      : %s" % rec.get("plan", "?"))
        print("  备注      : %s" % rec.get("remark", ""))
        if rec.get("revoked_at"):
            print("  状态      : 已作废于%s" % rec["revoked_at"][:19])
            return 0
        if key:
            kr = _kv._kv_get(KEY_PREFIX + key) or {}
            # 到期时间存在密钥记录里，不在订单记录里——
            # 之前从 rec 取会显示成「永久」，那是误导。
            if kr:
                print("  到期      : %s" % human_ttl(kr.get("expires_at")))
                print("  密钥状态  : 有效")
            else:
                print("  到期      : %s" % human_ttl(rec.get("expires_at")))
                print("  密钥状态  : Redis 中已无此密钥（过期回收或被误删）")
        return 0

    # ---- 作废 ----
    if args.revoke:
        rec = _kv._kv_get(order_key)
        if not rec:
            print("订单 %s 没有密钥记录，无需作废。" % order_id)
            return 0
        key = rec.get("key", "")
        print("将要作废：")
        print("  订单 %s" % order_id)
        print("  密钥 %s" % (key or "(空)"))
        if not args.commit:
            print("\n这是预览。确认无误后加 --commit 执行。")
            return 0
        # 订单记录里清掉 key，使其不再被幂等命中；密钥记录删掉，
        # 这样它连「已过期」都答不出来，只会 not_found。
        _kv._kv_set(order_key, dict(rec, key="", revoked_at=datetime.now().isoformat()),
                    ttl=ORDER_TTL_SECONDS)
        if key:
            _kv._rest("POST", "", ["DEL", KEY_PREFIX + key])
        print("已作废。该密钥现在会被判定为无效。")
        return 0

    # ---- 查重（发放前的核心检查）----
    existing = _kv._kv_get(order_key)
    if existing and existing.get("key"):
        print("订单 %s 已经发过密钥，不会重复发放。" % order_id)
        print("  密钥: %s" % existing["key"])
        print("  套餐: %s" % existing.get("plan", "?"))
        print("\n如果上次邮件没发出去，直接把上面这个密钥再发一次即可。")
        print("若需重新生成，用 --revoke 先作废旧的。")
        return 0

    plan = args.plan
    expires_at = _expiry_for(plan)
    days = _plan_duration_days(plan)
    key = generate_pro_key()

    record = {
        "plan": plan,
        "remark": args.note[:200],
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at,
    }
    order_record = {
        "key": key,
        "plan": plan,
        "amount": args.amount,
        "remark": args.note[:200],
        "created_at": datetime.now().isoformat(),
        "issued_by": "manual",
    }

    print("=" * 62)
    print("将要发放：")
    print("  订单号    : %s" % order_id)
    print("  密钥      : %s" % key)
    print("  套餐      : %s" % plan)
    print("  有效期    : %s"
          % ("永久" if days is None else "%d 天" % days))
    if days is not None:
        print("  到期时间  : %s" % human_ttl(expires_at))
    if args.amount:
        print("  金额      : %s" % args.amount)
    if args.note:
        print("  备注      : %s" % args.note)
    print("=" * 62)

    if not args.commit:
        print("\n这是预览，未写入任何数据。")
        print("确认无误后执行：")
        print("  python scripts/issue_key.py --order %s --plan %s --commit%s"
              % (order_id, plan, " --note \"%s\"" % args.note if args.note else ""))
        print("\n发放后把密钥发给用户即可，用户在任意工具页点「升级 Pro」输入它。")
        return 0

    try:
        _kv._kv_set(KEY_PREFIX + key, record, ttl=_key_ttl_seconds(expires_at))
        _kv._kv_set(order_key, order_record, ttl=ORDER_TTL_SECONDS)
    except _kv.KVError as exc:
        print("写入失败：%s" % exc)
        print("密钥 %s 未生效，请勿发给用户。" % key)
        return 1

    print("\n已写入存储。把下面这行发给用户：\n")
    print("    %s" % key)
    print("\n用户的使用方式：打开任意 AI 工具页 → 点「升级 Pro」→ 输入密钥。")
    return 0


if __name__ == "__main__":
    sys.exit(main())