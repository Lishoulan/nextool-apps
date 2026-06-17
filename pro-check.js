/**
 * NexTool Pro 密钥验证系统
 * 替代原有的 localStorage 限制，使用服务端验证
 * 使用方式：在 AI 工具页面引入此脚本即可
 *
 * <script src="https://lishoulan.github.io/nextool-apps/pro-check.js"></script>
 */

const NEXTOOL_PRO = {
    API_BASE: '',  // 空字符串 = 同域部署（API和静态页面在同一Vercel项目）
    LOCAL_KEY: 'nextool_pro_key',
    LOCAL_EXPIRY: 'nextool_pro_expiry',
    LOCAL_PLAN: 'nextool_pro_plan',
    FREE_LIMIT: 3,  // 每日免费次数

    // 获取存储的 Pro Key
    getKey() {
        return localStorage.getItem(this.LOCAL_KEY) || '';
    },

    // 保存 Pro Key
    saveKey(key, expiry, plan) {
        localStorage.setItem(this.LOCAL_KEY, key);
        localStorage.setItem(this.LOCAL_EXPIRY, expiry || '');
        localStorage.setItem(this.LOCAL_PLAN, plan || '');
    },

    // 清除 Pro Key
    clearKey() {
        localStorage.removeItem(this.LOCAL_KEY);
        localStorage.removeItem(this.LOCAL_EXPIRY);
        localStorage.removeItem(this.LOCAL_PLAN);
    },

    // 检查本地缓存的 Pro 状态（快速判断，不调API）
    isProLocal() {
        const key = this.getKey();
        if (!key) return false;
        const expiry = localStorage.getItem(this.LOCAL_EXPIRY);
        if (expiry && new Date(expiry) < new Date()) {
            this.clearKey();
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
            const data = await resp.json();

            if (data.valid) {
                this.saveKey(key, data.expires_at, data.plan);
                return { valid: true, plan: data.plan, expires_at: data.expires_at };
            } else {
                this.clearKey();
                return { valid: false, reason: data.reason || 'invalid' };
            }
        } catch (e) {
            // 网络错误时用本地缓存
            return { valid: this.isProLocal(), reason: 'offline_fallback' };
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
                        <a href="https://afdian.com/a/nextool-apps" target="_blank" 
                            style="color:#667eea;text-decoration:none;font-size:14px;">
                            没有密钥？去爱发电获取 →
                        </a>
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
