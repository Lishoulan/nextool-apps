/**
 * NexTool - 跨产品推荐组件
 * 在任意产品页底部展示"相关工具"推荐卡片
 *
 * 用法:
 * <div id="product-recommendations"></div>
 * <script src="./js/product-recommendations.js" data-current="ai-contract"></script>
 */
(function () {
  var products = [
    { id: 'pdf-toolkit', name: 'PDF工具箱', emoji: '📄', desc: '合并、拆分、压缩、转图片', url: './pdf-toolkit/' },
    { id: 'ai-resume', name: 'AI简历优化', emoji: '🎯', desc: '3分钟优化简历，通过率提升300%', url: './ai-resume-optimizer/' },
    { id: 'ai-ppt', name: 'AI PPT生成器', emoji: '📊', desc: '输入主题，10秒出完整幻灯片', url: './ai-ppt-generator/' },
    { id: 'ai-contract', name: 'AI合同生成器', emoji: '⚖️', desc: '1分钟生成专业法律合同', url: './ai-contract-generator/' },
    { id: 'ai-email', name: 'AI邮件写作器', emoji: '✉️', desc: '10种场景一键生成邮件', url: './ai-email-writer/' },
    { id: 'ai-paper', name: 'AI论文降重', emoji: '📝', desc: '一键降低查重率', url: './ai-paper-rewriter/' },
    { id: 'ai-translate', name: 'AI翻译工具', emoji: '🌐', desc: '8种语言智能翻译', url: './ai-translator/' },
    { id: 'ai-code', name: 'AI代码解释器', emoji: '💻', desc: '看不懂的代码秒懂', url: './ai-code-explainer/' },
    { id: 'ai-summarizer', name: 'AI文本摘要', emoji: '📋', desc: '免费！一键生成文章摘要', url: './ai-summarizer/' },
    { id: 'json-formatter', name: 'JSON格式化', emoji: '🔧', desc: '免费！格式化、验证、查询', url: './json-formatter/' },
    { id: 'qr-generator', name: '二维码生成器', emoji: '📱', desc: '免费！自定义颜色批量生成', url: './qr-generator/' },
    { id: 'pricing', name: '全站套餐', emoji: '💎', desc: '¥199/月全部无限使用', url: './pricing/' },
  ];

  // 获取当前产品ID
  var scriptEl = document.currentScript || document.querySelector('script[src*="product-recommendations"]');
  var currentId = scriptEl ? scriptEl.getAttribute('data-current') : '';

  // 过滤当前产品，随机选取4-6个
  var others = products.filter(function (p) { return p.id !== currentId; });
  var shuffled = others.sort(function () { return 0.5 - Math.random(); });
  var shown = shuffled.slice(0, Math.min(6, shuffled.length));

  // 构建HTML
  var cardsHtml = shown.map(function (p) {
    return '<a class="pr-card" href="' + p.url + '">' +
      '<span class="pr-card-emoji">' + p.emoji + '</span>' +
      '<span class="pr-card-name">' + p.name + '</span>' +
      '<span class="pr-card-desc">' + p.desc + '</span>' +
    '</a>';
  }).join('');

  var html =
    '<div class="pr-section">' +
      '<h3 class="pr-title">相关工具推荐</h3>' +
      '<div class="pr-grid">' + cardsHtml + '</div>' +
      '<a class="pr-view-all" href="./">查看全部工具 →</a>' +
    '</div>';

  // 注入样式
  var style = document.createElement('style');
  style.textContent =
    '.pr-section{max-width:960px;margin:3rem auto 0;padding:2rem 1.5rem;}' +
    '.pr-title{font-size:1.3rem;font-weight:700;color:#f0f0f5;margin-bottom:1.2rem;text-align:center;}' +
    '.pr-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;}' +
    '.pr-card{display:flex;flex-direction:column;align-items:flex-start;padding:1.2rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;text-decoration:none;color:#f0f0f5;transition:all .25s ease;backdrop-filter:blur(8px);}' +
    '.pr-card:hover{transform:translateY(-3px);border-color:#3a7bd5;box-shadow:0 6px 24px rgba(58,123,213,0.25);}' +
    '.pr-card-emoji{font-size:1.8rem;margin-bottom:.6rem;}' +
    '.pr-card-name{font-size:1rem;font-weight:600;margin-bottom:.3rem;}' +
    '.pr-card-desc{font-size:.82rem;color:#a0a0b8;line-height:1.4;}' +
    '.pr-view-all{display:block;text-align:center;margin-top:1.5rem;color:#3a7bd5;font-size:.95rem;text-decoration:none;transition:color .2s;}' +
    '.pr-view-all:hover{color:#00d2ff;}' +
    '@media(max-width:480px){.pr-grid{grid-template-columns:1fr 1fr;}.pr-card{padding:1rem;}.pr-card-emoji{font-size:1.4rem;}}';
  document.head.appendChild(style);

  // 注入DOM
  var container = document.getElementById('product-recommendations');
  if (container) {
    container.innerHTML = html;
  }
})();
