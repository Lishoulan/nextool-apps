# 手工发放 Pro 密钥 · 操作手册

给站长的 SOP。方案 A 的全部依据：**爱发电的 webhook 推送不带签名，无法验明来源**，所以不用自动回调，改为在后台看到付款后手工发密钥。

---

## 一、一次性准备（只做一次）

### 1. 注册 Upstash 并拿到凭据

到 console.upstash.io 新建一个 Database（免费层 10000 命令/日，够用），复制两个值。

### 2. 配好环境变量

在 Git Bash 里写进 `~/.bashrc`（每次开终端都可用，**不要提交进仓库**）：

```bash
export UPSTASH_REDIS_REST_URL='https://你的域名.upstash.io'
export UPSTASH_REDIS_REST_TOKEN='你的token'
```

验证：

```bash
cd /path/to/nextool-apps
python -c "import sys; sys.path.insert(0,'api'); import _kv; print(_kv._kv_get('probe'))"
```

打印 `None` 就是通了（能连上，只是这个 key 不存在）。报 `RuntimeError: Upstash 未配置` 说明环境变量没生效。

### 3. 在 Vercel 也配一份

Vercel 项目 → Settings → Environment Variables，加上同样那两个变量。
**这一步不能省** —— 网页上的密钥校验走 Vercel 上的 API，不是你的本机。

改完**必须 redeploy**，Vercel 不会热重载环境变量。

---

## 二、日常流程：收到一笔付款

### 第 1 步：拿到订单号

爱发电后台 → 订单列表 → 复制**订单号**（对应 API 里的 `out_trade_no`，一串数字）。

### 第 2 步：先预览

```bash
cd /path/to/nextool-apps
python scripts/issue_key.py --order 2026100622001 --plan monthly --note "张先生 微信付19"
```

**不加 `--commit` 不写入任何东西**，只是预览。确认订单号、套餐、备注都对再往下走。

套餐对应：

| 卖价 | `--plan` | 有效期 |
|---|---|---|
| ¥19（月付） | `monthly` | 30 天 |
| 年付 | `yearly` | 365 天 |
| 永久 | `lifetime` | 永久 |

### 第 3 步：确认写入

```bash
python scripts/issue_key.py --order 2026100622001 --plan monthly --note "张先生 微信付19" --commit
```

输出给你一行密钥：

```
    NTP-XXXX-XXXX-XXXX
```

### 第 4 步：发给用户

把这行密钥发给用户，告诉他：在任意 AI 工具页点「升级 Pro」→ 粘贴 → 激活。

用户侧界面已改好，弹窗里有一段折叠的「已付款？这样拿密钥」，会告诉他从订单号发邮件到 `service@nextool.cn` 来取。所以邮件里写清订单号即可。

---

## 三、常见情况

**邮件发失败 / 不确定上次有没有发** —— 直接重跑同一条命令。同一个订单号不会产生第二个密钥，而是把原来那个打印出来：

```
订单 2026100622001 已经发过密钥，不会重复发放。
  密钥: NTP-1120-6F7D-D27C
```

放心重发。

**查发放状态**

```bash
python scripts/issue_key.py --order 2026100622001 --check
```

显示密钥、套餐、到期时间、密钥当前是否还有效。

**退款了 / 发错了要作废**

```bash
python scripts/issue_key.py --order 2026100622001 --revoke        # 预览
python scripts/issue_key.py --order 2026100622001 --revoke --commit  # 执行
```

作废后该密钥立刻失效。之后要重发直接再跑发放命令 —— 作废时把订单记录里的 key 清空了，幂等检查不会拦住。

---

## 四、这个方案的边界

**规模上限：每月 20–30 单。** 超过就忙不过来了，那时做方案 B（订单号自助查密钥页面）或 C（邮件自动发送）。

**已知安全权衡**：webhook 无签名，所以 `/api/afdian/webhook` 无法验明请求来自爱发电 —— 知道 URL 和订单号的人可伪造订单骗密钥。**方案 A 下这个端点不应对外暴露**，实际上也没人会去调它。哪天要启用自动回调，得改用爱发电的**主动查询 API**（那条链路有签名）。

**密钥交付仍靠人工** —— 这是方案 A 的定义。

---

## 五、前提：Vercel 必须先恢复

⚠️ **Vercel 上的 API 服务当前处于宕机状态**（TCP 连 443 超时）。密钥发出去后，用户在网页上激活时 `/api/pro/verify` 会不通。

去 vercel.com/dashboard 看 `nextool-api-proxy-vercel` 项目：

| 症状 | 处理 |
|---|---|
| 显示 "Paused" / 已暂停 | 点 Resume |
| 有未付账单 | 补上 |
| 项目不存在 | 只能重建：导入仓库 → 自动识别 `vercel.json` → 补环境变量 |

重建后项目名要保持 `nextool-api-proxy-vercel`，否则 `pro-check.js:10` 的 `API_BASE` 域名对不上（域名变了要同步改）。

---

## 六、命令速查

```bash
python scripts/issue_key.py --order <订单号> --plan monthly                      # 预览
python scripts/issue_key.py --order <订单号> --plan monthly --note "备注" --commit  # 发放
python scripts/issue_key.py --order <订单号> --check                              # 查询
python scripts/issue_key.py --order <订单号> --revoke --commit                   # 作废
```

带中文备注用双引号：`--note "张先生 微信付19"`。`--amount` 和 `--note` 只作记录，不影响发放。