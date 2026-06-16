/**
 * NexTool 统一支付模块 - 面包多集成
 * 使用方法：在页面中引入此脚本，调用 NexToolPay.openCheckout(productKey)
 *
 * 面包多商品链接配置 - 替换为你的真实商品链接
 * 注册地址：https://mianbaoduo.com
 */
const NexToolPay = {
  // ===== 商品配置 =====
  // TODO: 注册面包多后，替换为你的真实商品链接
  products: {
    'ppt-pro': {
      name: 'AI PPT 生成器 Pro',
      price: '¥49/月',
      // 面包多商品链接 - 替换为你创建的商品URL
      checkoutUrl: 'https://mianbaoduo.com/o/REPLACE_PPT_PRO',
      features: ['无限次生成', '5-20页幻灯片', '4种风格模板', 'HTML导出', '优先响应速度']
    },
    'translator-pro': {
      name: 'AI 翻译 Pro',
      price: '¥19/月',
      checkoutUrl: 'https://mianbaoduo.com/o/REPLACE_TRANSLATOR_PRO',
      features: ['无限翻译次数', '8种语言互译', '4种翻译风格', '翻译历史记录']
    },
    'email-pro': {
      name: 'AI 邮件写作 Pro',
      price: '¥19/月',
      checkoutUrl: 'https://mianbaoduo.com/o/REPLACE_EMAIL_PRO',
      features: ['无限生成次数', '多种邮件风格', '一键复制发送', '历史记录']
    },
    'resume-pro': {
      name: 'AI 简历优化 Pro',
      price: '¥29/月',
      checkoutUrl: 'https://mianbaoduo.com/o/REPLACE_RESUME_PRO',
      features: ['无限优化次数', '岗位匹配分析', '关键词优化', 'ATS友好格式']
    },
    'all-tools': {
      name: 'NexTool 全家桶',
      price: '¥99/月',
      checkoutUrl: 'https://mianbaoduo.com/o/REPLACE_ALL_TOOLS',
      features: ['所有Pro工具无限使用', 'PPT/翻译/邮件/简历', '优先客服支持', '新工具优先体验']
    }
  },

  // ===== Pro 状态管理 =====
  _storageKey: 'nextool_pro_status',

  getProStatus() {
    try {
      const data = JSON.parse(localStorage.getItem(this._storageKey) || '{}');
      // 检查是否过期
      if (data.expiry && Date.now() > data.expiry) {
        this.setProStatus(false);
        return { active: false };
      }
      return { active: !!data.active, expiry: data.expiry, product: data.product };
    } catch {
      return { active: false };
    }
  },

  setProStatus(active, productKey, daysValid = 30) {
    const data = {
      active,
      product: productKey,
      expiry: active ? Date.now() + daysValid * 86400000 : 0,
      activatedAt: active ? Date.now() : 0
    };
    localStorage.setItem(this._storageKey, JSON.stringify(data));
  },

  isPro(productKey) {
    const status = this.getProStatus();
    if (!status.active) return false;
    // 全家桶用户所有产品都可用
    if (status.product === 'all-tools') return true;
    // 特定产品用户
    return status.product === productKey;
  },

  // ===== 支付流程 =====
  openCheckout(productKey) {
    const product = this.products[productKey];
    if (!product) {
      console.error('NexToolPay: 未知产品', productKey);
      return;
    }

    // 检查是否已经是Pro
    if (this.isPro(productKey)) {
      this.showToast('您已是Pro用户，无需重复购买', 'success');
      return;
    }

    // 打开面包多支付页面
    // 面包多支持回调URL，支付成功后可以自动激活
    const callbackUrl = encodeURIComponent(window.location.href + '?paid=1&product=' + productKey);
    const payUrl = product.checkoutUrl + '?callback=' + callbackUrl;

    // 在新窗口打开支付
    window.open(payUrl, '_blank');

    // 同时显示提示弹窗
    this.showPaymentConfirmModal(productKey);
  },

  // ===== 支付确认弹窗 =====
  showPaymentConfirmModal(productKey) {
    const product = this.products[productKey];
    if (!product) return;

    // 移除已有弹窗
    const existing = document.getElementById('nextool-pay-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'nextool-pay-modal';
    modal.innerHTML = `
      <div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:10000;display:flex;align-items:center;justify-content:center;padding:20px;">
        <div style="background:#1a1a2e;border:1px solid #2a2a4a;border-radius:16px;padding:32px;max-width:420px;width:100%;color:#e8e8f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;">
          <h2 style="font-size:20px;font-weight:700;margin-bottom:8px;">完成支付</h2>
          <p style="color:#8888aa;font-size:14px;margin-bottom:20px;">支付完成后，点击下方按钮激活Pro</p>
          <div style="background:#16162a;border:1px solid #2a2a4a;border-radius:12px;padding:16px;margin-bottom:20px;">
            <div style="font-size:16px;font-weight:600;margin-bottom:4px;">${product.name}</div>
            <div style="font-size:24px;font-weight:800;background:linear-gradient(135deg,#6c5ce7,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">${product.price}</div>
            <ul style="margin-top:12px;font-size:13px;color:#8888aa;list-style:none;padding:0;">
              ${product.features.map(f => '<li style="padding:3px 0">✓ ' + f + '</li>').join('')}
            </ul>
          </div>
          <button onclick="NexToolPay.confirmPayment('${productKey}')" style="width:100%;padding:12px;background:linear-gradient(135deg,#6c5ce7,#a855f7);color:#fff;border:none;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer;margin-bottom:8px;">我已完成支付，激活Pro</button>
          <button onclick="NexToolPay.closeModal()" style="width:100%;padding:10px;background:transparent;color:#8888aa;border:1px solid #2a2a4a;border-radius:8px;font-size:13px;cursor:pointer;">稍后再说</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  },

  confirmPayment(productKey) {
    // 在实际生产中，这里应该调用后端验证支付状态
    // 目前先用本地激活（面包多支付成功后会跳回带参数的页面）
    this.setProStatus(true, productKey);
    this.closeModal();
    this.showToast('Pro 已激活！感谢您的支持', 'success');
    // 刷新页面状态
    setTimeout(() => window.location.reload(), 1000);
  },

  closeModal() {
    const modal = document.getElementById('nextool-pay-modal');
    if (modal) modal.remove();
  },

  // ===== URL 回调检测 =====
  checkPaymentCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('paid') === '1') {
      const product = urlParams.get('product');
      if (product && this.products[product]) {
        this.setProStatus(true, product);
        this.showToast('支付成功！Pro 已激活', 'success');
        // 清除URL参数
        window.history.replaceState({}, '', window.location.pathname);
        return true;
      }
    }
    return false;
  },

  // ===== Toast 提示 =====
  showToast(message, type = 'success') {
    const existing = document.getElementById('nextool-pay-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'nextool-pay-toast';
    const bgColor = type === 'success' ? 'rgba(34,197,94,0.9)' : 'rgba(239,68,68,0.9)';
    toast.style.cssText = `position:fixed;bottom:24px;right:24px;background:${bgColor};color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:20000;transform:translateY(80px);opacity:0;transition:all .3s;`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
      toast.style.transform = 'translateY(0)';
      toast.style.opacity = '1';
    });

    setTimeout(() => {
      toast.style.transform = 'translateY(80px)';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
};

// 页面加载时自动检测支付回调
document.addEventListener('DOMContentLoaded', () => {
  NexToolPay.checkPaymentCallback();
});
