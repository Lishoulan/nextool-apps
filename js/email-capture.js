/**
 * NexTool Email Capture Widget
 * 可配置的浮动邮件捕获组件，用于在任何产品页面收集用户邮箱
 *
 * 使用方法：
 * <script src="./js/email-capture.js"></script>
 *
 * 配置示例：
 * <script>
 *   EmailCapture.init({
 *     title: '获取5个免费积分',
 *     creditAmount: 5,
 *     position: 'bottom-right',  // bottom-right | bottom-left
 *     delay: 5000,               // 延迟显示（毫秒）
 *     showOncePerDay: true        // 每天只显示一次
 *   });
 * </script>
 */

(function(global) {
    'use strict';

    const STORAGE_KEY = 'nextool_emails';
    const CREDITS_KEY = 'nextool_credits';
    const SHOWN_KEY = 'nextool_email_capture_shown_date';

    const defaultConfig = {
        title: '🎉 获取5个免费积分',
        subtitle: '输入邮箱即可领取，可用于任意 AI 工具',
        creditAmount: 5,
        position: 'bottom-right',
        delay: 5000,
        showOncePerDay: true,
        buttonText: '🎁 免费领取',
        placeholder: '请输入您的邮箱',
        submitText: '立即领取',
        successTitle: '🎉 恭喜！',
        successMessage: '{credits} 个免费积分已到账！',
        theme: 'dark'
    };

    let config = {};
    let widgetCreated = false;

    function deepMerge(target, source) {
        const result = Object.assign({}, target);
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                result[key] = deepMerge(result[key] || {}, source[key]);
            } else {
                result[key] = source[key];
            }
        }
        return result;
    }

    function getStoredEmails() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        } catch { return []; }
    }

    function saveEmail(email) {
        const emails = getStoredEmails();
        const exists = emails.some(e => e.email === email);
        if (!exists) {
            emails.push({
                email: email,
                timestamp: new Date().toISOString(),
                source: window.location.pathname,
                creditsAwarded: config.creditAmount
            });
            localStorage.setItem(STORAGE_KEY, JSON.stringify(emails));
            return true;
        }
        return false;
    }

    function addCredits(amount) {
        const current = parseInt(localStorage.getItem(CREDITS_KEY) || '0', 10);
        localStorage.setItem(CREDITS_KEY, (current + amount).toString());
    }

    function wasShownToday() {
        const shownDate = localStorage.getItem(SHOWN_KEY);
        if (!shownDate) return false;
        const today = new Date().toISOString().slice(0, 10);
        return shownDate === today;
    }

    function markShownToday() {
        localStorage.setItem(SHOWN_KEY, new Date().toISOString().slice(0, 10));
    }

    function injectStyles() {
        if (document.getElementById('nextool-email-capture-styles')) return;

        const style = document.createElement('style');
        style.id = 'nextool-email-capture-styles';
        style.textContent = `
            .nextool-fab {
                position: fixed;
                bottom: 24px;
                ${config.position === 'bottom-left' ? 'left' : 'right'}: 24px;
                z-index: 9998;
                background: linear-gradient(135deg, #f0b90b, #fcd535);
                color: #0f0f23;
                border: none;
                border-radius: 50px;
                padding: 14px 24px;
                font-size: 15px;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(240,185,11,0.4);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
                animation: nextool-fab-in 0.5s ease;
            }

            @keyframes nextool-fab-in {
                from { opacity: 0; transform: translateY(20px) scale(0.9); }
                to { opacity: 1; transform: translateY(0) scale(1); }
            }

            .nextool-fab:hover {
                transform: translateY(-3px) scale(1.03);
                box-shadow: 0 8px 30px rgba(240,185,11,0.5);
            }

            .nextool-fab:active {
                transform: translateY(-1px) scale(1);
            }

            .nextool-fab .fab-icon {
                font-size: 20px;
                line-height: 1;
            }

            .nextool-overlay {
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.6);
                backdrop-filter: blur(4px);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }

            .nextool-overlay.show {
                opacity: 1;
                visibility: visible;
            }

            .nextool-modal {
                background: linear-gradient(160deg, #1a1a3e, #0f0f23);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 2.5rem 2rem;
                max-width: 420px;
                width: 90%;
                text-align: center;
                transform: scale(0.9) translateY(20px);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
            }

            .nextool-overlay.show .nextool-modal {
                transform: scale(1) translateY(0);
            }

            .nextool-modal .modal-close {
                position: absolute;
                top: 12px;
                right: 16px;
                background: none;
                border: none;
                color: #6c6c80;
                font-size: 24px;
                cursor: pointer;
                padding: 4px;
                line-height: 1;
                transition: color 0.2s;
            }

            .nextool-modal .modal-close:hover {
                color: #f0f0f5;
            }

            .nextool-modal .modal-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                display: block;
            }

            .nextool-modal h3 {
                color: #f0f0f5;
                font-size: 1.4rem;
                margin-bottom: 0.5rem;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }

            .nextool-modal p {
                color: #a0a0b8;
                font-size: 0.95rem;
                margin-bottom: 1.5rem;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }

            .nextool-modal .input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 1rem;
            }

            .nextool-modal input[type="email"] {
                flex: 1;
                padding: 12px 16px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.06);
                color: #f0f0f5;
                font-size: 15px;
                outline: none;
                transition: border-color 0.3s, box-shadow 0.3s;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }

            .nextool-modal input[type="email"]:focus {
                border-color: #f0b90b;
                box-shadow: 0 0 0 3px rgba(240,185,11,0.15);
            }

            .nextool-modal input[type="email"]::placeholder {
                color: #6c6c80;
            }

            .nextool-modal .submit-btn {
                padding: 12px 24px;
                border-radius: 10px;
                border: none;
                background: linear-gradient(135deg, #f0b90b, #fcd535);
                color: #0f0f23;
                font-weight: 700;
                font-size: 15px;
                cursor: pointer;
                transition: all 0.3s;
                white-space: nowrap;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }

            .nextool-modal .submit-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 15px rgba(240,185,11,0.4);
            }

            .nextool-modal .submit-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }

            .nextool-modal .disclaimer {
                color: #6c6c80;
                font-size: 0.75rem;
                margin-top: 0.5rem;
            }

            .nextool-modal .success-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
                display: block;
                animation: nextool-bounce 0.6s ease;
            }

            @keyframes nextool-bounce {
                0% { transform: scale(0); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }

            .nextool-toast {
                position: fixed;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%) translateY(20px);
                background: #00d4aa;
                color: #0f0f23;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                opacity: 0;
                transition: all 0.4s ease;
                z-index: 10001;
                pointer-events: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }

            .nextool-toast.show {
                transform: translateX(-50%) translateY(0);
                opacity: 1;
            }

            @media (max-width: 480px) {
                .nextool-fab {
                    bottom: 16px;
                    ${config.position === 'bottom-left' ? 'left' : 'right'}: 16px;
                    padding: 12px 18px;
                    font-size: 14px;
                }
                .nextool-modal {
                    padding: 2rem 1.5rem;
                }
                .nextool-modal .input-group {
                    flex-direction: column;
                }
            }
        `;
        document.head.appendChild(style);
    }

    function createWidget() {
        if (widgetCreated) return;
        widgetCreated = true;

        // FAB Button
        const fab = document.createElement('button');
        fab.className = 'nextool-fab';
        fab.innerHTML = `<span class="fab-icon">🎁</span> ${config.buttonText}`;
        fab.addEventListener('click', showModal);
        document.body.appendChild(fab);

        // Overlay + Modal
        const overlay = document.createElement('div');
        overlay.className = 'nextool-overlay';
        overlay.id = 'nextool-email-overlay';
        overlay.innerHTML = `
            <div class="nextool-modal">
                <button class="modal-close" onclick="EmailCapture.hide()">&times;</button>
                <div id="nextool-form-view">
                    <span class="modal-icon">🎁</span>
                    <h3>${config.title}</h3>
                    <p>${config.subtitle}</p>
                    <div class="input-group">
                        <input type="email" id="nextool-email-input" placeholder="${config.placeholder}" autocomplete="email">
                        <button class="submit-btn" id="nextool-submit-btn" onclick="EmailCapture.submit()">${config.submitText}</button>
                    </div>
                    <p class="disclaimer">我们尊重您的隐私，不会发送垃圾邮件</p>
                </div>
                <div id="nextool-success-view" style="display:none;">
                    <span class="success-icon">✅</span>
                    <h3>${config.successTitle}</h3>
                    <p>${config.successMessage.replace('{credits}', config.creditAmount)}</p>
                </div>
            </div>
        `;
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) EmailCapture.hide();
        });
        document.body.appendChild(overlay);

        // Toast
        const toast = document.createElement('div');
        toast.className = 'nextool-toast';
        toast.id = 'nextool-toast';
        document.body.appendChild(toast);

        // Enter key support
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && document.getElementById('nextool-email-input') === document.activeElement) {
                EmailCapture.submit();
            }
            if (e.key === 'Escape') {
                EmailCapture.hide();
            }
        });
    }

    function showModal() {
        const overlay = document.getElementById('nextool-email-overlay');
        if (overlay) {
            overlay.classList.add('show');
            setTimeout(() => {
                const input = document.getElementById('nextool-email-input');
                if (input) input.focus();
            }, 300);
        }

        // Track in GA
        if (typeof gtag === 'function') {
            gtag('event', 'email_capture_shown', { source: window.location.pathname });
        }
    }

    function hideModal() {
        const overlay = document.getElementById('nextool-email-overlay');
        if (overlay) overlay.classList.remove('show');
    }

    function showToast(msg) {
        const toast = document.getElementById('nextool-toast');
        if (!toast) return;
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2500);
    }

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function submitEmail() {
        const input = document.getElementById('nextool-email-input');
        const email = input ? input.value.trim() : '';

        if (!email || !validateEmail(email)) {
            showToast('⚠️ 请输入有效的邮箱地址');
            return;
        }

        const btn = document.getElementById('nextool-submit-btn');
        if (btn) btn.disabled = true;

        const isNew = saveEmail(email);

        if (isNew) {
            addCredits(config.creditAmount);
            markShownToday();

            // Show success view
            const formView = document.getElementById('nextool-form-view');
            const successView = document.getElementById('nextool-success-view');
            if (formView) formView.style.display = 'none';
            if (successView) successView.style.display = 'block';

            showToast(`🎉 ${config.creditAmount} 个免费积分已到账！`);

            // Track in GA
            if (typeof gtag === 'function') {
                gtag('event', 'email_captured', {
                    source: window.location.pathname,
                    credits: config.creditAmount
                });
            }

            // Auto close after 3 seconds
            setTimeout(() => {
                EmailCapture.hide();
                // Reset for next time
                setTimeout(() => {
                    if (formView) formView.style.display = 'block';
                    if (successView) successView.style.display = 'none';
                    if (input) input.value = '';
                    if (btn) btn.disabled = false;
                }, 300);
            }, 3000);
        } else {
            showToast('✅ 该邮箱已注册过，积分已到账');
            setTimeout(() => EmailCapture.hide(), 1500);
            if (btn) btn.disabled = false;
        }
    }

    // ===== Public API =====
    const EmailCapture = {
        init: function(userConfig) {
            config = deepMerge(defaultConfig, userConfig || {});
            injectStyles();

            // Check if should show
            if (config.showOncePerDay && wasShownToday()) {
                // Still create the FAB but don't auto-show modal
                createWidget();
                return;
            }

            // Create widget after delay
            setTimeout(() => {
                createWidget();
                // Auto-show modal after FAB appears
                setTimeout(() => {
                    if (!wasShownToday()) {
                        showModal();
                    }
                }, 2000);
            }, config.delay);
        },

        show: showModal,
        hide: hideModal,
        submit: submitEmail,

        // Utility: get all collected emails
        getEmails: function() {
            return getStoredEmails();
        },

        // Utility: get current credits
        getCredits: function() {
            return parseInt(localStorage.getItem(CREDITS_KEY) || '0', 10);
        },

        // Utility: export emails (for backend integration)
        exportEmails: function() {
            const emails = getStoredEmails();
            const csv = 'Email,Timestamp,Source,Credits\n' +
                emails.map(e => `${e.email},${e.timestamp},${e.source},${e.creditsAwarded}`).join('\n');
            return csv;
        },

        // Utility: send emails to backend
        sendToBackend: function(url) {
            const emails = getStoredEmails();
            if (!emails.length) return Promise.resolve({ success: true, message: 'No emails to send' });

            return fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emails: emails })
            }).then(r => r.json());
        },

        // Reset (for testing)
        reset: function() {
            localStorage.removeItem(SHOWN_KEY);
            widgetCreated = false;
            const fab = document.querySelector('.nextool-fab');
            const overlay = document.getElementById('nextool-email-overlay');
            const toast = document.getElementById('nextool-toast');
            if (fab) fab.remove();
            if (overlay) overlay.remove();
            if (toast) toast.remove();
        }
    };

    // Expose globally
    global.EmailCapture = EmailCapture;

    // Auto-init with defaults if data-auto attribute is present
    if (document.currentScript && document.currentScript.hasAttribute('data-auto')) {
        document.addEventListener('DOMContentLoaded', function() {
            EmailCapture.init();
        });
    }

})(window);
