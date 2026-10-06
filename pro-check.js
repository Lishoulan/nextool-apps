/**
 * NexTool Pro 密钥验证系统
 * 替代原有的 localStorage 限制，使用服务端验证
 * 使用方式：在 AI 工具页面引入此脚本即可
 *
 * <script src="https://lishoulan.github.io/nextool-apps/pro-check.js"></script>
 */

const NEXTOOL_PRO = {
    // API 与静态页面不在同一个域：站点在 GitHub Pages，API 在 Vercel。
    // 之前这里是空字符串，请求打到 https://lishoulan.github.io/api/pro/verify
    // 被 Pages 当静态文件处理，返回 405，catch 又回退到 isProLocal()。
    API_BASE: 'https://nextool-api-proxy-vercel.vercel.app',
    LOCAL_KEY: 'nextool_pro_key',
    LOCAL_EXPIRY: 'nextool_pro_expiry',
    LOCAL_PLAN: 'nextool_pro_plan',
    // 服务端最后一次确认「这个密钥有效」的时间戳（毫秒）。
    // 没有它，localStorage 里的 key+expiry 就是两段用户自己也能写的字符串，
    // isProLocal() 会把它们当成付费凭据。7 天宽限用于 API 临时不可用时
    // 不让付费用户被误降级。
    LOCAL_VERIFIED: 'nextool_pro_verified_at',
    OFFLINE_GRACE_MS: 7 * 24 * 3600 * 1000,
    FREE_LIMIT: 3,  // 每日免费次数
    _verifiedOnline: false,

    // 获取存储的 Pro Key
    getKey() {
        return localStorage.getItem(this.LOCAL_KEY) || '';
    },

    // 保存 Pro Key
    saveKey(key, expiry, plan) {
        localStorage.setItem(this.LOCAL_KEY, key);
        localStorage.setItem(this.LOCAL_EXPIRY, expiry || '');
        localStorage.setItem(this.LOCAL_PLAN, plan || '');
        localStorage.setItem(this.LOCAL_VERIFIED, String(Date.now()));
    },

    // 清除 Pro Key
    clearKey() {
        localStorage.removeItem(this.LOCAL_KEY);
        localStorage.removeItem(this.LOCAL_EXPIRY);
        localStorage.removeItem(this.LOCAL_PLAN);
        localStorage.removeItem(this.LOCAL_VERIFIED);
    },

    // 存量用户迁移：服务端的盖章字段是本次新增的，已经付费的用户
    // localStorage 里只有 key+expiry，没有 verified_at。
    //
    // 关键约束：只在「服务端此刻不可用」时才给本地宽限。
    // 如果服务端能答，就让它答——否则这道迁移就退化成一个后门：
    // 谁都能手写一个格式合法的 key 换到 7 天 Pro。
    // 所以这个函数**不做**自动盖章，只在 offline 分支里被显式调用。
    //
    // 诚实的边界：即便如此，expiry 与 verified_at 都在 localStorage，
    // 愿意改控制台的人仍能伪造。真正不可绕过的位置是 /api/chat。
    migrateLegacyKey() {
        const key = this.getKey();
        if (!key) return false;
        if (localStorage.getItem(this.LOCAL_VERIFIED)) return false;
        const expiry = localStorage.getItem(this.LOCAL_EXPIRY);
        if (/^NTP-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}$/i.test(key) && expiry) {
            localStorage.setItem(this.LOCAL_VERIFIED, String(Date.now()));
            return true;
        }
        return false;
    },

    // 检查本地缓存的 Pro 状态（快速判断，不调API）。
    // 只读服务端盖章，不自行迁移——迁移仅在 verifyPro 确认服务端不可用后进行。
    isProLocal() {
        const key = this.getKey();
        if (!key) return false;
        const expiry = localStorage.getItem(this.LOCAL_EXPIRY);
        if (expiry && new Date(expiry) < new Date()) {
            this.clearKey();
            return false;
        }
        // 没有服务端盖章、或盖章已超出宽限期，一律不认。
        // 少了这一条，用户只要往 localStorage 写个 key 就能得 Pro。
        const verified = parseInt(localStorage.getItem(this.LOCAL_VERIFIED) || '0', 10);
        if (!verified || (Date.now() - verified) > this.OFFLINE_GRACE_MS) {
            return false;
        }
        return true;
    },

    // 服务端验证 Pro Key（异步）
    async verifyPro() {
        const key = this.getKey();
        if (!key) return { valid: false, reason: 'no_key' };

        try {
            const resp = await fetch(`${this.API_BASE}/api/pro/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key })
            });

            // 服务端本身不可用（502/503/404/405 或反向代理挡了）时，
            // 不能当成「密钥无效」——那会把付费用户的凭据清掉。
            // 这种情况退回本地宽限票据。
            if (resp.status >= 500 || resp.status === 404 || resp.status === 405) {
                this._verifiedOnline = false;
                // 服务端此刻答不上来，才允许存量用户走本地迁移宽限。
                this.migrateLegacyKey();
                return { valid: this.isProLocal(), reason: 'offline' };
            }

            const data = await resp.json();

            if (data.valid) {
                this._verifiedOnline = true;
                this.saveKey(key, data.expires_at, data.plan);
                return { valid: true, plan: data.plan, expires_at: data.expires_at };
            }

            // 服务端明确说这个密钥无效：这是权威结论，
            // 离线宽限在此失效——宁可让用户重新输一次密钥，
            // 也不能让一个已被吊销的密钥靠本地缓存续命。
            this._verifiedOnline = true;
            this.clearKey();
            return { valid: false, reason: data.reason || 'invalid' };
        } catch (e) {
            this._verifiedOnline = false;
            this.migrateLegacyKey();
            return { valid: this.isProLocal(), reason: 'offline' };
        }
    },

    // 激活 Pro Key
    async activateKey(key) {
        try {
            const resp = await fetch(`${this.API_BASE}/api/pro/activate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key })
            });
            const data = await resp.json();

            if (data.valid) {
                this.saveKey(key, data.expires_at, data.plan);
                return { success: true, message: data.message };
            } else {
                return { success: false, reason: data.reason, message: data.reason === 'expired' ? '密钥已过期' : '密钥无效' };
            }
        } catch (e) {
            return { success: false, reason: 'network_error', message: '网络错误，请稍后重试' };
        }
    },

    // 检查使用次数（免费用户）
    getUsageToday() {
        const today = new Date().toDateString();
        const stored = localStorage.getItem('nextool_usage_' + today);
        return stored ? parseInt(stored) : 0;
    },

    // 记录一次使用
    recordUsage() {
        const today = new Date().toDateString();
        const current = this.getUsageToday();
        localStorage.setItem('nextool_usage_' + today, (current + 1).toString());
    },

    // 检查是否可以使用（核心函数）
    async canUse() {
        // Pro 用户无限制
        if (this.isProLocal()) {
            const result = await this.verifyPro();
            if (result.valid) return { allowed: true, is_pro: true };
        }

        // 免费用户检查次数
        const used = this.getUsageToday();
        if (used < this.FREE_LIMIT) {
            return { allowed: true, is_pro: false, remaining: this.FREE_LIMIT - used - 1 };
        }

        return { allowed: false, is_pro: false, remaining: 0, need_pro: true };
    },

    // 显示 Pro 激活弹窗
    showProModal(reason) {
        // 如果已有弹窗则不重复
        if (document.getElementById('nextool-pro-modal')) return;

        const isExpired = reason === 'expired';
        const modal = document.createElement('div');
        modal.id = 'nextool-pro-modal';
        modal.innerHTML = `
            <div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:99999;display:flex;align-items:center;justify-content:center;">
                <div style="background:#1a1a2e;border-radius:16px;padding:32px;max-width:420px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.5);">
                    <div style="font-size:48px;margin-bottom:12px;">⭐</div>
                    <h2 style="color:#fff;margin:0 0 8px;font-size:22px;">${isExpired ? 'Pro 已过期' : '升级 NexTool Pro'}</h2>
                    <p style="color:#aaa;margin:0 0 20px;font-size:14px;">${isExpired ? '您的Pro密钥已过期，请续费或输入新密钥' : '每日免费使用3次，升级Pro无限使用'}</p>
                    <div style="margin-bottom:16px;">
                        <input id="nextool-pro-input" type="text" placeholder="输入Pro密钥 (NTP-XXXX-XXXX-XXXX)" 
                            style="width:100%;padding:12px;border:1px solid #333;border-radius:8px;background:#0f0f1a;color:#fff;font-size:14px;box-sizing:border-box;"
                        />
                    </div>
                    <button id="nextool-pro-activate" style="width:100%;padding:12px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;margin-bottom:12px;">
                        激活 Pro
                    </button>
                    <div style="margin-bottom:12px;">
                        <a href="https://afdian.com/a/nextool-apps" target="_blank" rel="noopener"
                            style="color:#667eea;text-decoration:none;font-size:14px;">
                            还没有？先在爱发电购买 →
                        </a>
                        <div id="nextool-pro-howto" style="display:none;margin-top:10px;font-size:12.5px;color:#777;line-height:1.7;">
                            <strong style="color:#999;">已付款？这样拿密钥：</strong><br>
                            1. 在爱发电「我的订单」里复制订单号<br>
                            2. 发邮件到
                            <a href="mailto:service@nextool.cn?subject=Pro%20密钥%20申请&body=%E6%88%91%E5%B7%B2%E6%94%AF%E4%BB%98%EF%BC%8C%E8%AF%B7%E5%8F%91%E6%88%91%E8%AE%A2%E5%8D%95%E5%8F%B7%EF%BC%9A"
                               style="color:#667eea;">service@nextool.cn</a>
                            ，主题写「Pro 密钥申请」<br>
                            3. 收到回复后把密钥粘贴到上面输入框
                            <button id="nextool-pro-howto-toggle" type="button"
                                style="display:block;margin-top:6px;background:none;border:none;color:#667eea;cursor:pointer;font-size:12px;padding:0;">
                                我已付款，查看取密钥步骤
                            </button>
                        </div>
                    </div>
                    <button id="nextool-pro-close" style="background:none;border:none;color:#666;cursor:pointer;font-size:13px;">
                        暂不升级，继续使用免费版
                    </button>
                    <div id="nextool-pro-status" style="margin-top:12px;font-size:13px;color:#aaa;"></div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // 激活按钮
        document.getElementById('nextool-pro-activate').onclick = async () => {
            const key = document.getElementById('nextool-pro-input').value.trim();
            const statusEl = document.getElementById('nextool-pro-status');
            if (!key) {
                statusEl.textContent = '请输入Pro密钥';
                statusEl.style.color = '#ff6b6b';
                return;
            }
            statusEl.textContent = '验证中...';
            statusEl.style.color = '#aaa';

            const result = await NEXTOOL_PRO.activateKey(key);
            if (result.success) {
                statusEl.textContent = '✅ ' + result.message;
                statusEl.style.color = '#51cf66';
                setTimeout(() => {
                    modal.remove();
                    // 刷新页面以更新状态
                    if (typeof __nextoolOnProActivated === 'function') {
                        __nextoolOnProActivated();
                    }
                }, 1000);
            } else {
                statusEl.textContent = '❌ ' + result.message;
                statusEl.style.color = '#ff6b6b';
            }
        };

        // 「已付款？这样拿密钥」折叠区
        const howto = document.getElementById('nextool-pro-howto');
        const howtoBtn = document.getElementById('nextool-pro-howto-toggle');
        if (howto && howtoBtn) {
            howtoBtn.onclick = () => {
                const shown = howto.style.display !== 'none';
                howto.style.display = shown ? 'none' : 'block';
                howtoBtn.textContent = shown
                    ? '我已付款，查看取密钥步骤'
                    : '收起';
            };
        }

        // 关闭按钮
        document.getElementById('nextool-pro-close').onclick = () => {
            modal.remove();
        };

        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal.firstElementChild.parentElement) {
                modal.remove();
            }
        };
    },

    // 显示 Pro 状态指示器（右上角）
    showProBadge() {
        if (document.getElementById('nextool-pro-badge')) return;

        const isPro = this.isProLocal();
        const badge = document.createElement('div');
        badge.id = 'nextool-pro-badge';
        badge.style.cssText = 'position:fixed;top:12px;right:12px;z-index:99998;font-size:12px;padding:4px 10px;border-radius:12px;cursor:pointer;';
        badge.style.background = isPro ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#333';
        badge.style.color = '#fff';
        badge.textContent = isPro ? '⭐ Pro' : `免费 ${this.getUsageToday()}/${this.FREE_LIMIT}`;
        badge.title = isPro ? 'NexTool Pro 已激活' : '点击升级 Pro';
        badge.onclick = () => this.showProModal(isPro ? '' : 'limit');
        document.body.appendChild(badge);
    }
};

// 自动显示 Pro 状态
document.addEventListener('DOMContentLoaded', () => {
    NEXTOOL_PRO.showProBadge();
});
