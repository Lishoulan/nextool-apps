/**
 * NextTool - 社交分享按钮组件
 * 在产品页底部展示分享按钮，支持微信/微博/Twitter/复制链接
 *
 * 用法:
 * <div id="social-share" data-title="页面标题" data-url="页面URL"></div>
 * <script src="../js/social-share.js"></script>
 */
(function () {
  var container = document.getElementById('social-share');
  if (!container) return;

  var title = container.getAttribute('data-title') || document.title;
  var url = container.getAttribute('data-url') || window.location.href;
  var encodedUrl = encodeURIComponent(url);
  var encodedTitle = encodeURIComponent(title);

  var platforms = [
    {
      name: '微信',
      icon: '💬',
      color: '#07c160',
      action: 'wechat'
    },
    {
      name: '微博',
      icon: '📢',
      color: '#e6162d',
      action: 'weibo'
    },
    {
      name: 'Twitter',
      icon: '🐦',
      color: '#1da1f2',
      action: 'twitter'
    },
    {
      name: '复制链接',
      icon: '🔗',
      color: '#6c757d',
      action: 'copy'
    }
  ];

  var buttonsHtml = platforms.map(function (p) {
    return '<button class="ss-btn" data-action="' + p.action + '" style="--btn-color:' + p.color + '">' +
      '<span class="ss-icon">' + p.icon + '</span>' +
      '<span class="ss-name">' + p.name + '</span>' +
    '</button>';
  }).join('');

  var html =
    '<div class="ss-section">' +
      '<h3 class="ss-title">觉得好用？分享给朋友</h3>' +
      '<div class="ss-buttons">' + buttonsHtml + '</div>' +
      '<div class="ss-wechat-tip" id="ssWechatTip" style="display:none">' +
        '<p>截图或长按下方二维码分享到微信</p>' +
        '<div class="ss-qrcode" id="ssQrcode"></div>' +
        '<button class="ss-close-tip" onclick="document.getElementById(\'ssWechatTip\').style.display=\'none\'">关闭</button>' +
      '</div>' +
    '</div>';

  // Inject styles
  var style = document.createElement('style');
  style.textContent =
    '.ss-section{max-width:600px;margin:2rem auto 0;padding:1.5rem;text-align:center;}' +
    '.ss-title{font-size:1rem;color:#aaa;margin-bottom:1rem;font-weight:500;}' +
    '.ss-buttons{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;}' +
    '.ss-btn{display:flex;align-items:center;gap:6px;padding:10px 18px;border:1px solid rgba(255,255,255,0.15);border-radius:10px;background:rgba(255,255,255,0.05);color:#ccc;font-size:0.85rem;cursor:pointer;transition:all .25s ease;backdrop-filter:blur(8px);}' +
    '.ss-btn:hover{border-color:var(--btn-color);color:#fff;box-shadow:0 4px 16px rgba(0,0,0,0.2);transform:translateY(-2px);}' +
    '.ss-icon{font-size:1.1rem;}' +
    '.ss-name{font-weight:500;}' +
    '.ss-wechat-tip{margin-top:1rem;padding:1.5rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;}' +
    '.ss-wechat-tip p{color:#aaa;font-size:0.85rem;margin-bottom:1rem;}' +
    '.ss-qrcode{width:160px;height:160px;margin:0 auto;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;}' +
    '.ss-close-tip{margin-top:1rem;padding:6px 16px;border:1px solid rgba(255,255,255,0.15);border-radius:8px;background:transparent;color:#aaa;font-size:0.8rem;cursor:pointer;}';
  document.head.appendChild(style);

  container.innerHTML = html;

  // Handle clicks
  container.addEventListener('click', function (e) {
    var btn = e.target.closest('.ss-btn');
    if (!btn) return;
    var action = btn.getAttribute('data-action');

    switch (action) {
      case 'wechat':
        document.getElementById('ssWechatTip').style.display = 'block';
        // Generate QR code using a simple canvas approach
        var qrDiv = document.getElementById('ssQrcode');
        if (qrDiv && !qrDiv.hasChildNodes()) {
          var qrImg = document.createElement('img');
          qrImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + encodedUrl;
          qrImg.alt = 'QR Code';
          qrImg.style.width = '150px';
          qrImg.style.height = '150px';
          qrImg.style.borderRadius = '4px';
          qrDiv.appendChild(qrImg);
        }
        break;
      case 'weibo':
        window.open('https://service.weibo.com/share/share.php?url=' + encodedUrl + '&title=' + encodedTitle, '_blank', 'width=600,height=500');
        break;
      case 'twitter':
        window.open('https://twitter.com/intent/tweet?url=' + encodedUrl + '&text=' + encodedTitle, '_blank', 'width=600,height=400');
        break;
      case 'copy':
        navigator.clipboard.writeText(url).then(function () {
          btn.querySelector('.ss-name').textContent = '已复制!';
          setTimeout(function () { btn.querySelector('.ss-name').textContent = '复制链接'; }, 2000);
        }).catch(function () {
          // Fallback
          var ta = document.createElement('textarea');
          ta.value = url;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          btn.querySelector('.ss-name').textContent = '已复制!';
          setTimeout(function () { btn.querySelector('.ss-name').textContent = '复制链接'; }, 2000);
        });
        break;
    }
  });
})();
