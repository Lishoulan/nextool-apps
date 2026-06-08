/**
 * NextTool - AdSense广告位组件
 * 在免费工具页面展示广告位，实现免费用户变现
 *
 * 用法:
 * <div class="nextool-ad" data-slot="top" data-format="horizontal"></div>
 * <script src="../js/adsense-component.js"></script>
 *
 * data-slot: top/bottom/sidebar/inline
 * data-format: horizontal/vertical/rectangle
 */
(function () {
  // AdSense publisher ID - replace with your actual ID
  var ADSENSE_ID = 'ca-pub-XXXXXXXXXXXXXXXX';

  var adSlots = {
    top: { format: 'horizontal', label: '广告', height: '90px' },
    middle: { format: 'rectangle', label: '广告', height: '250px' },
    bottom: { format: 'horizontal', label: '广告', height: '90px' },
    sidebar: { format: 'vertical', label: '广告', height: '250px' },
    inline: { format: 'rectangle', label: '广告', height: '250px' }
  };

  // Google Analytics event tracking
  function trackAdEvent(action, slot, format) {
    if (typeof gtag === 'function') {
      gtag('event', action, {
        'event_category': 'Ad',
        'event_label': slot + '_' + format
      });
    } else if (typeof dataLayer !== 'undefined') {
      dataLayer.push({
        'event': action,
        'event_category': 'Ad',
        'event_label': slot + '_' + format
      });
    }
  }

  // Inject styles
  var style = document.createElement('style');
  style.textContent =
    '.nextool-ad{max-width:728px;margin:1rem auto;text-align:center;position:relative;}' +
    '.nextool-ad-inner{background:rgba(255,255,255,0.03);border:1px dashed rgba(255,255,255,0.1);border-radius:8px;overflow:hidden;min-height:90px;display:flex;align-items:center;justify-content:center;position:relative;}' +
    '.nextool-ad-label{position:absolute;top:4px;left:8px;font-size:0.65rem;color:#555;text-transform:uppercase;letter-spacing:0.5px;}' +
    '.nextool-ad-placeholder{color:#444;font-size:0.8rem;padding:1rem;}' +
    '.nextool-ad[data-format="vertical"] .nextool-ad-inner{min-height:250px;max-width:300px;margin:0 auto;}' +
    '.nextool-ad[data-format="rectangle"] .nextool-ad-inner{min-height:250px;max-width:336px;margin:0 auto;}';
  document.head.appendChild(style);

  // Process all ad containers
  document.querySelectorAll('.nextool-ad').forEach(function (adEl) {
    var slot = adEl.getAttribute('data-slot') || 'inline';
    var format = adEl.getAttribute('data-format') || 'horizontal';
    var config = adSlots[slot] || adSlots.inline;

    adEl.setAttribute('data-format', format);

    // Track ad impression
    trackAdEvent('ad_impression', slot, format);

    // If AdSense is configured, show real ad
    if (ADSENSE_ID !== 'ca-pub-XXXXXXXXXXXXXXXX') {
      var ins = document.createElement('ins');
      ins.className = 'adsbygoogle';
      ins.style.display = 'block';
      ins.setAttribute('data-ad-client', ADSENSE_ID);
      ins.setAttribute('data-ad-slot', slot);
      ins.setAttribute('data-ad-format', 'auto');
      ins.setAttribute('data-full-width-responsive', 'true');
      
      // Add click tracking
      adEl.addEventListener('click', function() {
        trackAdEvent('ad_click', slot, format);
      });
      
      adEl.innerHTML = '';
      adEl.appendChild(ins);
      (adsbygoogle = window.adsbygoogle || []).push({});
    } else {
      // Show placeholder until AdSense is configured
      var placeholder = document.createElement('div');
      placeholder.className = 'nextool-ad-inner';
      placeholder.innerHTML = 
        '<span class="nextool-ad-label">' + config.label + '</span>' +
        '<div class="nextool-ad-placeholder">Ad 广告位<br><small>配置 AdSense 后显示</small></div>';
      
      // Add click tracking to placeholder
      placeholder.addEventListener('click', function() {
        trackAdEvent('ad_click', slot, format);
      });
      
      adEl.innerHTML = '';
      adEl.appendChild(placeholder);
    }
  });

  // Load AdSense script if configured
  if (ADSENSE_ID !== 'ca-pub-XXXXXXXXXXXXXXXX') {
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADSENSE_ID;
    script.crossOrigin = 'anonymous';
    document.head.appendChild(script);
  }
})();
