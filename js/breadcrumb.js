/**
 * NextTool - 面包屑导航组件
 * 在产品页顶部显示面包屑，提升SEO和用户体验
 *
 * 用法:
 * <div id="breadcrumb" data-product="AI PPT生成器"></div>
 * <script src="../js/breadcrumb.js"></script>
 */
(function () {
  var container = document.getElementById('breadcrumb');
  if (!container) return;

  var productName = container.getAttribute('data-product') || document.title.split(' - ')[0] || '工具';
  var baseUrl = 'https://lishoulan.github.io/nextool-apps/';

  // Inject structured data
  var schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "首页",
        "item": baseUrl
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": productName
      }
    ]
  };

  var schemaScript = document.createElement('script');
  schemaScript.type = 'application/ld+json';
  schemaScript.textContent = JSON.stringify(schema);
  document.head.appendChild(schemaScript);

  // Inject styles
  var style = document.createElement('style');
  style.textContent =
    '.bc-nav{display:flex;align-items:center;gap:6px;padding:10px 0;font-size:0.82rem;flex-wrap:wrap;}' +
    '.bc-nav a{color:#888;text-decoration:none;transition:color .2s;}' +
    '.bc-nav a:hover{color:#3a7bd5;}' +
    '.bc-sep{color:#555;font-size:0.7rem;}' +
    '.bc-current{color:#ccc;font-weight:500;}';
  document.head.appendChild(style);

  // Build breadcrumb HTML
  var html =
    '<nav class="bc-nav" aria-label="面包屑导航">' +
      '<a href="../">🏠 首页</a>' +
      '<span class="bc-sep">›</span>' +
      '<span class="bc-current">' + productName + '</span>' +
    '</nav>';

  container.innerHTML = html;
})();
