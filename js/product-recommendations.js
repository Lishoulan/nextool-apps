/**
 * NexTool - 跨产品推荐组件
 * 在任意产品页底部展示"相关工具"推荐卡片
 *
 * 用法:
 * <div id="product-recommendations"></div>
 * <script src="./js/product-recommendations.js" data-current="ai-contract-generator"></script>
 */
(function () {
  // ── 产品列表（22个） ──
  var products = [
    // AI 付费工具
    { id: 'pdf-toolkit',           name: 'PDF工具箱',      emoji: '📄', desc: '合并/拆分/压缩/转图片6大功能',       url: './pdf-toolkit/',           cat: 'ai' },
    { id: 'ai-resume-optimizer',  name: 'AI简历优化器',   emoji: '🎯', desc: 'AI智能优化简历，面试通过率提升80%',   url: './ai-resume-optimizer/',   cat: 'ai', hot: true },
    { id: 'ai-ppt-generator',     name: 'AI PPT生成器',   emoji: '📊', desc: 'AI一键生成专业PPT',                  url: './ai-ppt-generator/',      cat: 'ai', hot: true },
    { id: 'ai-contract-generator',name: 'AI合同生成器',   emoji: '⚖️', desc: '12种合同类型智能生成',               url: './ai-contract-generator/', cat: 'ai', hot: true },
    { id: 'ai-email-writer',     name: 'AI邮件写作器',   emoji: '✉️', desc: '10种场景一键生成邮件',               url: './ai-email-writer/',       cat: 'ai' },
    { id: 'ai-paper-rewriter',   name: '论文降重助手',   emoji: '📝', desc: 'AI智能改写降低查重率',               url: './ai-paper-rewriter/',     cat: 'ai' },
    { id: 'ai-translator',       name: 'AI翻译工具',     emoji: '🌐', desc: '8种语言智能翻译',                    url: './ai-translator/',         cat: 'ai' },
    { id: 'ai-code-explainer',   name: 'AI代码解释器',   emoji: '💻', desc: '30+编程语言逐行解释',                url: './ai-code-explainer/',     cat: 'ai' },
    { id: 'ai-summarizer',       name: 'AI文本摘要',     emoji: '📋', desc: '免费TextRank摘要',                  url: './ai-summarizer/',         cat: 'free' },
    // 免费工具
    { id: 'json-formatter',      name: 'JSON格式化',     emoji: '🔧', desc: '免费验证美化压缩',                   url: './json-formatter/',        cat: 'free' },
    { id: 'qr-generator',        name: '二维码生成器',   emoji: '📱', desc: '免费自定义批量生成',                 url: './qr-generator/',          cat: 'free' },
    { id: 'regex-tester',        name: '正则测试器',     emoji: '🔍', desc: '免费实时匹配高亮',                   url: './regex-tester/',          cat: 'free' },
    { id: 'color-picker',        name: '颜色选择器',     emoji: '🎨', desc: '免费HEX/RGB/HSL转换',               url: './color-picker/',          cat: 'free' },
    { id: 'markdown-editor',     name: 'Markdown编辑器', emoji: '📝', desc: '免费实时预览',                       url: './markdown-editor/',       cat: 'free' },
    { id: 'base64-tool',         name: 'Base64编解码',   emoji: '🔐', desc: '免费文本图片互转',                   url: './base64-tool/',           cat: 'free' },
    { id: 'url-tool',            name: 'URL编解码',      emoji: '🔗', desc: '免费参数解析编辑',                   url: './url-tool/',              cat: 'free' },
    { id: 'timestamp-tool',      name: '时间戳转换',     emoji: '⏱️', desc: '免费多时区转换',                     url: './timestamp-tool/',         cat: 'free' },
    { id: 'password-generator',  name: '密码生成器',     emoji: '🔑', desc: '免费随机强密码生成',                 url: './password-generator/',    cat: 'free' },
    { id: 'word-counter',        name: '字数统计',       emoji: '📊', desc: '免费中英文词频分析',                 url: './word-counter/',           cat: 'free' },
    { id: 'image-compressor',    name: '图片压缩',       emoji: '🖼️', desc: '免费批量压缩不失真',                 url: './image-compressor/',       cat: 'free' },
    { id: 'calculator',          name: '在线计算器',     emoji: '🧮', desc: '免费科学计算+单位换算',               url: './calculator/',             cat: 'free' },
    // 套餐
    { id: 'pricing',             name: '全站套餐',       emoji: '💎', desc: '¥199/月全部无限使用',                 url: './pricing/',                cat: 'pricing' },
  ];

  // ── 获取当前产品ID ──
  var scriptEl = document.currentScript || document.querySelector('script[src*="product-recommendations"]');
  var currentId = scriptEl ? scriptEl.getAttribute('data-current') : '';

  // ── 判断当前产品类别 ──
  var currentProduct = products.find(function (p) { return p.id === currentId; });
  var currentCat = currentProduct ? currentProduct.cat : '';

  // ── 交叉推荐逻辑：在免费工具页优先推荐AI工具，在AI工具页优先推荐免费工具 ──
  var others = products.filter(function (p) { return p.id !== currentId; });

  var prioritized, rest;
  if (currentCat === 'free') {
    // 当前是免费工具 → 优先推荐AI付费工具
    prioritized = others.filter(function (p) { return p.cat === 'ai'; });
    rest = others.filter(function (p) { return p.cat !== 'ai'; });
  } else if (currentCat === 'ai') {
    // 当前是AI工具 → 优先推荐免费工具
    prioritized = others.filter(function (p) { return p.cat === 'free'; });
    rest = others.filter(function (p) { return p.cat !== 'free'; });
  } else {
    // 默认：AI工具优先
    prioritized = others.filter(function (p) { return p.cat === 'ai'; });
    rest = others.filter(function (p) { return p.cat !== 'ai'; });
  }

  // 热门推荐排在最前面
  prioritized.sort(function (a, b) { return (b.hot ? 1 : 0) - (a.hot ? 1 : 0); });

  var shown = prioritized.concat(rest).slice(0, 6);

  // ── 构建卡片HTML ──
  var cardsHtml = shown.map(function (p) {
    var badges = '';
    if (p.hot) {
      badges += '<span class="pr-badge pr-badge-hot">热门推荐</span>';
    }
    if (p.cat === 'free') {
      badges += '<span class="pr-badge pr-badge-free">免费</span>';
    }
    return '<a class="pr-card" href="' + p.url + '">' +
      '<span class="pr-card-emoji">' + p.emoji + '</span>' +
      '<span class="pr-card-name">' + p.name + badges + '</span>' +
      '<span class="pr-card-desc">' + p.desc + '</span>' +
    '</a>';
  }).join('');

  // ── CTA横幅 ──
  var ctaHtml = '<a class="pr-cta" href="./pricing/">' +
    '<span class="pr-cta-text">🔓 解锁全部AI工具</span>' +
    '<span class="pr-cta-price">→ ¥199/月</span>' +
  '</a>';

  // ── 组装完整HTML ──
  var html =
    '<div class="pr-section">' +
      '<h3 class="pr-title">相关工具推荐</h3>' +
      '<div class="pr-grid">' + cardsHtml + '</div>' +
      ctaHtml +
      '<a class="pr-view-all" href="./">查看全部工具 →</a>' +
    '</div>';

  // ── 注入样式 ──
  var style = document.createElement('style');
  style.textContent =
    '.pr-section{max-width:960px;margin:3rem auto 0;padding:2rem 1.5rem;}' +
    '.pr-title{font-size:1.3rem;font-weight:700;color:#f0f0f5;margin-bottom:1.2rem;text-align:center;}' +
    '.pr-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;}' +
    '.pr-card{display:flex;flex-direction:column;align-items:flex-start;padding:1.2rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;text-decoration:none;color:#f0f0f5;transition:all .25s ease;backdrop-filter:blur(8px);position:relative;}' +
    '.pr-card:hover{transform:translateY(-3px);border-color:#3a7bd5;box-shadow:0 6px 24px rgba(58,123,213,0.25);}' +
    '.pr-card-emoji{font-size:1.8rem;margin-bottom:.6rem;}' +
    '.pr-card-name{font-size:1rem;font-weight:600;margin-bottom:.3rem;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;}' +
    '.pr-card-desc{font-size:.82rem;color:#a0a0b8;line-height:1.4;}' +
    /* 徽章样式 */
    '.pr-badge{display:inline-block;font-size:.65rem;font-weight:600;padding:1px 6px;border-radius:4px;line-height:1.5;vertical-align:middle;}' +
    '.pr-badge-hot{background:linear-gradient(135deg,#ff6b6b,#ee5a24);color:#fff;}' +
    '.pr-badge-free{background:rgba(0,210,150,0.15);color:#00d296;border:1px solid rgba(0,210,150,0.3);}' +
    /* CTA横幅 */
    '.pr-cta{display:flex;align-items:center;justify-content:center;gap:.6rem;margin-top:1.5rem;padding:1rem 1.5rem;background:linear-gradient(135deg,#3a7bd5,#00d2ff);border-radius:12px;text-decoration:none;color:#fff;font-weight:600;font-size:1.05rem;transition:all .25s ease;box-shadow:0 4px 16px rgba(58,123,213,0.3);}' +
    '.pr-cta:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(58,123,213,0.45);}' +
    '.pr-cta-text{font-size:1.05rem;}' +
    '.pr-cta-price{font-size:1.1rem;font-weight:700;}' +
    '.pr-view-all{display:block;text-align:center;margin-top:1.5rem;color:#3a7bd5;font-size:.95rem;text-decoration:none;transition:color .2s;}' +
    '.pr-view-all:hover{color:#00d2ff;}' +
    '@media(max-width:480px){.pr-grid{grid-template-columns:1fr 1fr;}.pr-card{padding:1rem;}.pr-card-emoji{font-size:1.4rem;}.pr-cta{font-size:.95rem;padding:.85rem 1rem;}}';
  document.head.appendChild(style);

  // ── 注入DOM ──
  var container = document.getElementById('product-recommendations');
  if (container) {
    container.innerHTML = html;
  }
})();
