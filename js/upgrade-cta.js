/**
 * NexTool Upgrade CTA - 智能升级引导组件
 * 在所有AI工具页面添加多维度转化元素：
 *   1. 浮动升级按钮（右下角常驻）
 *   2. 社会证明通知（左下角轮播）
 *   3. 使用次数指示器（右上角）
 *   4. 底部升级横幅（使用2次后显示）
 *   5. 信任标识栏
 *
 * 用法:
 * <script src="../js/upgrade-cta.js" data-tool="ai-email-writer" data-limit="3"></script>
 */
(function() {
  'use strict';

  var script = document.currentScript || document.querySelector('script[src*="upgrade-cta"]');
  var toolName = script ? script.getAttribute('data-tool') : 'AI工具';
  var limit = parseInt(script ? script.getAttribute('data-limit') : '3', 10) || 3;
  var AFDIAN = 'https://afdian.com/a/nextool-apps';
  var USAGE_KEY = 'nextool-usage';

  // ===== 1. Social Proof Notifications =====
  var socialProofMessages = [
    '北京用户 刚刚升级了 Pro 版',
    '上海用户 刚刚生成了一份报告',
    '深圳用户 刚刚完成了工作优化',
    '杭州用户 刚刚升级了 Pro 会员',
    '广州用户 刚刚使用了高级功能',
    '成都用户 刚刚节省了2小时工作时间',
    '武汉用户 刚刚升级了 Pro 版',
    '南京用户 今天已使用 12 次'
  ];

  function createSocialProof() {
    var container = document.createElement('div');
    container.id = 'nextool-social-proof';
    container.style.cssText = 'position:fixed;bottom:24px;left:24px;z-index:9997;max-width:320px;pointer-events:none;';
    document.body.appendChild(container);

    var idx = Math.floor(Math.random() * socialProofMessages.length);
    function showNotification() {
      var msg = socialProofMessages[idx % socialProofMessages.length];
      idx++;
      container.innerHTML = '';
      var el = document.createElement('div');
      el.style.cssText = 'background:rgba(22,22,31,0.95);border:1px solid rgba(108,92,231,0.3);border-radius:12px;padding:12px 18px;display:flex;align-items:center;gap:10px;backdrop-filter:blur(10px);animation:ntSlideIn 0.4s ease;pointer-events:auto;cursor:pointer;';
      el.innerHTML = '<span style="font-size:1.2em;">⚡</span><span style="color:#c8c8d8;font-size:0.85rem;line-height:1.4;">' + msg + '</span>';
      el.onclick = function() { window.open(AFDIAN, '_blank'); };
      container.appendChild(el);

      setTimeout(function() {
        el.style.transition = 'opacity 0.4s, transform 0.4s';
        el.style.opacity = '0';
        el.style.transform = 'translateY(10px)';
        setTimeout(function() { el.remove(); }, 400);
      }, 4000);
    }

    // Show first after 8s, then every 15s
    setTimeout(function() {
      showNotification();
      setInterval(showNotification, 15000);
    }, 8000);
  }

  // ===== 2. Floating Upgrade Button =====
  function createFloatingCTA() {
    // Don't create if one already exists
    if (document.getElementById('nextool-upgrade-fab')) return;

    var fab = document.createElement('a');
    fab.id = 'nextool-upgrade-fab';
    fab.href = AFDIAN;
    fab.target = '_blank';
    fab.rel = 'noopener';
    fab.innerHTML = '<span>⭐</span> 升级 Pro · ¥9.9/首月';
    fab.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9998;display:flex;align-items:center;gap:8px;padding:12px 22px;background:linear-gradient(135deg,#6c5ce7,#a855f7);color:#fff;border-radius:50px;text-decoration:none;font-size:14px;font-weight:600;box-shadow:0 4px 20px rgba(108,92,231,0.4);transition:transform 0.25s,box-shadow 0.25s;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;';
    fab.onmouseover = function() {
      this.style.transform = 'translateY(-3px)';
      this.style.boxShadow = '0 8px 30px rgba(108,92,231,0.6)';
    };
    fab.onmouseout = function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 4px 20px rgba(108,92,231,0.4)';
    };
    document.body.appendChild(fab);
  }

  // ===== 3. Usage Indicator =====
  function createUsageIndicator() {
    // Don't duplicate if one already exists
    if (document.getElementById('nextool-usage-ind')) return;

    var usage = getUsage();
    var remaining = Math.max(0, limit - usage.count);
    var color = remaining <= 1 ? '#ff6b6b' : remaining <= 2 ? '#f0b90b' : '#a855f7';

    var ind = document.createElement('div');
    ind.id = 'nextool-usage-ind';
    ind.style.cssText = 'position:fixed;top:10px;right:10px;z-index:9998;background:rgba(22,22,31,0.92);border:1px solid rgba(108,92,231,0.25);border-radius:20px;padding:6px 14px;font-size:12px;color:#9a9aaa;backdrop-filter:blur(8px);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;';
    ind.innerHTML = '今日已用 <span style="color:' + color + ';font-weight:700;">' + usage.count + '</span>/' + limit +
      (remaining > 0
        ? ' · <a href="' + AFDIAN + '" target="_blank" style="color:#6c5ce7;text-decoration:none;font-weight:600;">升级Pro</a>'
        : ' · <a href="' + AFDIAN + '" target="_blank" style="color:#ff6b6b;text-decoration:none;font-weight:700;">⚡立即升级</a>');
    document.body.appendChild(ind);
  }

  // ===== 4. Smart Bottom Banner =====
  function createBottomBanner() {
    var usage = getUsage();
    // Only show after 2 uses (user is engaged)
    if (usage.count < 2) return;
    if (document.getElementById('nextool-bottom-banner')) return;

    var banner = document.createElement('div');
    banner.id = 'nextool-bottom-banner';
    banner.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:9996;background:linear-gradient(135deg,rgba(108,92,231,0.95),rgba(168,85,247,0.95));backdrop-filter:blur(10px);padding:14px 20px;display:flex;align-items:center;justify-content:center;gap:16px;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;animation:ntBannerIn 0.5s ease;';

    var remaining = Math.max(0, limit - usage.count);
    var urgencyText = remaining <= 1
      ? '⚡ 今日仅剩 ' + remaining + ' 次免费使用'
      : '🎁 升级 Pro 解锁无限使用 + 全部高级功能';

    banner.innerHTML =
      '<span style="color:#fff;font-size:0.95rem;font-weight:600;">' + urgencyText + '</span>' +
      '<a href="' + AFDIAN + '" target="_blank" rel="noopener" style="display:inline-block;padding:8px 24px;background:#fff;color:#6c5ce7;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.9rem;transition:transform 0.2s;" onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'">⭐ ¥9.9/首月 升级</a>' +
      '<button onclick="this.parentElement.remove()" style="background:none;border:none;color:rgba(255,255,255,0.6);font-size:18px;cursor:pointer;padding:4px 8px;margin-left:4px;">✕</button>';

    document.body.appendChild(banner);

    // Adjust floating CTA position when banner is visible
    var fab = document.getElementById('nextool-upgrade-fab');
    if (fab) fab.style.bottom = '70px';
  }

  // ===== 5. Trust Badges =====
  function createTrustBadges() {
    if (document.getElementById('nextool-trust-badges')) return;

    var container = document.createElement('div');
    container.id = 'nextool-trust-badges';
    container.style.cssText = 'text-align:center;padding:16px 20px;display:flex;justify-content:center;gap:20px;flex-wrap:wrap;font-size:0.82rem;color:#888;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;';
    container.innerHTML =
      '<span>🔒 数据安全加密</span>' +
      '<span>⚡ AI 3秒出结果</span>' +
      '<span>⭐ 4.9/5 用户好评</span>' +
      '<span>👥 10,000+ 用户信赖</span>';
    // Insert before footer or at end of body
    var footer = document.querySelector('footer');
    if (footer) {
      footer.parentNode.insertBefore(container, footer);
    } else {
      document.body.appendChild(container);
    }
  }

  // ===== 6. Countdown Offer (限时优惠) =====
  function createCountdownOffer() {
    var storageKey = 'nextool_offer_dismissed';
    if (sessionStorage.getItem(storageKey)) return;

    // Only show after user has used the tool at least once
    var usage = getUsage();
    if (usage.count < 1) return;

    // Create a subtle countdown near the upgrade area
    var el = document.createElement('div');
    el.id = 'nextool-countdown-offer';
    el.style.cssText = 'position:fixed;top:50px;right:10px;z-index:9997;background:rgba(22,22,31,0.95);border:1px solid rgba(240,185,11,0.4);border-radius:12px;padding:12px 16px;max-width:220px;backdrop-filter:blur(10px);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;';

    // Generate a countdown that resets at midnight
    function getCountdown() {
      var now = new Date();
      var tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(0, 0, 0, 0);
      var diff = tomorrow - now;
      var h = Math.floor(diff / 3600000);
      var m = Math.floor((diff % 3600000) / 60000);
      var s = Math.floor((diff % 60000) / 1000);
      return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
    }

    el.innerHTML =
      '<div style="color:#f0b90b;font-size:0.8rem;font-weight:700;margin-bottom:6px;">🔥 今日限时特惠</div>' +
      '<div style="color:#e8e6e3;font-size:0.9rem;font-weight:600;margin-bottom:4px;">Pro 首月 ¥9.9</div>' +
      '<div id="nt-countdown" style="color:#ff6b6b;font-size:1.1rem;font-weight:800;font-family:monospace;margin-bottom:8px;">' + getCountdown() + '</div>' +
      '<a href="' + AFDIAN + '" target="_blank" rel="noopener" style="display:block;text-align:center;padding:8px;background:linear-gradient(135deg,#6c5ce7,#a855f7);color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;">立即抢购 →</a>' +
      '<button onclick="this.parentElement.remove();sessionStorage.setItem(\'nextool_offer_dismissed\',\'1\')" style="position:absolute;top:4px;right:8px;background:none;border:none;color:#666;font-size:14px;cursor:pointer;">✕</button>';

    document.body.appendChild(el);

    // Update countdown every second
    setInterval(function() {
      var cd = document.getElementById('nt-countdown');
      if (cd) cd.textContent = getCountdown();
    }, 1000);
  }

  // ===== Helper: Get Usage =====
  function getUsage() {
    try {
      var d = JSON.parse(localStorage.getItem(USAGE_KEY) || '{}');
      var today = new Date().toISOString().slice(0, 10);
      if (d.date !== today) return { date: today, count: 0 };
      return d;
    } catch (e) { return { date: new Date().toISOString().slice(0, 10), count: 0 }; }
  }

  // ===== Inject Animation Styles =====
  function injectStyles() {
    if (document.getElementById('nextool-upgrade-styles')) return;
    var s = document.createElement('style');
    s.id = 'nextool-upgrade-styles';
    s.textContent =
      '@keyframes ntSlideIn{from{opacity:0;transform:translateY(15px)}to{opacity:1;transform:translateY(0)}}' +
      '@keyframes ntBannerIn{from{opacity:0;transform:translateY(100%)}to{opacity:1;transform:translateY(0)}}' +
      '@keyframes ntPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.03)}}';
    document.head.appendChild(s);
  }

  // ===== Track GA Events =====
  function trackEvent(action, label) {
    if (typeof gtag === 'function') {
      gtag('event', action, { event_category: 'Upgrade', event_label: label || toolName });
    }
  }

  // ===== Init =====
  function init() {
    injectStyles();
    createFloatingCTA();
    createUsageIndicator();
    createSocialProof();
    createTrustBadges();

    // Delay bottom banner and countdown for better UX
    setTimeout(createBottomBanner, 3000);
    setTimeout(createCountdownOffer, 12000);

    // Track
    trackEvent('upgrade_cta_loaded', toolName);
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
