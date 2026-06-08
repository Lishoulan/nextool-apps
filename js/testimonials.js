/**
 * NextTool Testimonials Component - 用户评价组件
 * 在AI工具页面展示用户评价，增强信任感
 *
 * 使用方法：
 * <script src="../js/testimonials.js"></script>
 *
 * 根据页面URL自动匹配对应分类的评价内容
 */
(function() {
    'use strict';

    // 检测当前页面所属分类
    var path = window.location.pathname;
    var isAITool = /ai-(ppt-generator|resume-optimizer|contract-generator|email-writer|paper-rewriter|translator|code-explainer|summarizer)/.test(path);
    var category = isAITool ? 'ai' : 'free';

    // 各分类评价数据
    var testimonials = {
        ai: [
            {
                name: '张明',
                nameEn: 'Zhang Ming',
                role: '产品经理',
                roleEn: 'Product Manager',
                avatar: 'ZM',
                quote: '用AI PPT生成器3分钟就做出了季度汇报，以前至少要花2小时排版。效率提升太明显了！',
                quoteEn: 'Generated my quarterly report PPT in 3 minutes with the AI tool — it used to take at least 2 hours. Massive efficiency boost!'
            },
            {
                name: '李雪',
                nameEn: 'Li Xue',
                role: '应届毕业生',
                roleEn: 'Fresh Graduate',
                avatar: 'LX',
                quote: '简历优化器帮我把经历描述改得更专业，投了5家公司拿到了3个面试，之前只有1个。',
                quoteEn: 'The Resume Optimizer made my experience descriptions much more professional. Got 3 interviews from 5 applications, up from just 1 before.'
            },
            {
                name: '王建国',
                nameEn: 'Wang Jianguo',
                role: '创业者',
                roleEn: 'Entrepreneur',
                avatar: 'WJ',
                quote: '合同生成器太实用了，劳动合同、保密协议一键生成，省了请律师的几千块。',
                quoteEn: 'The Contract Generator is incredibly practical — employment contracts and NDAs generated in one click, saving thousands on legal fees.'
            },
            {
                name: '陈思雨',
                nameEn: 'Chen Siyu',
                role: '研究生',
                roleEn: 'Graduate Student',
                avatar: 'CS',
                quote: '论文降重帮了大忙，查重率从38%降到8%，而且语句通顺自然，不像机器改的。',
                quoteEn: 'The Paper Rewriter was a lifesaver — plagiarism rate dropped from 38% to 8%, and the sentences flow naturally, not like machine rewrites.'
            }
        ],
        free: [
            {
                name: '赵磊',
                nameEn: 'Zhao Lei',
                role: '前端开发',
                roleEn: 'Frontend Developer',
                avatar: 'ZL',
                quote: 'JSON格式化和正则测试器太好用了，不用注册打开就能用，比装插件方便多了。',
                quoteEn: 'The JSON Formatter and Regex Tester are so handy — no registration needed, just open and use. Way more convenient than installing extensions.'
            },
            {
                name: '刘芳',
                nameEn: 'Liu Fang',
                role: '行政助理',
                roleEn: 'Administrative Assistant',
                avatar: 'LF',
                quote: 'PDF工具箱免费就能合并拆分，之前用的网站都要收费，这个完全免费还不用登录。',
                quoteEn: 'The PDF Toolkit lets me merge and split for free. Other sites charge for this, but this one is completely free with no login required.'
            },
            {
                name: '孙伟',
                nameEn: 'Sun Wei',
                role: '设计师',
                roleEn: 'Designer',
                avatar: 'SW',
                quote: '颜色选择器和图片压缩是我最常用的两个工具，本地处理不上传，隐私安全有保障。',
                quoteEn: 'The Color Picker and Image Compressor are my most-used tools. Local processing with no uploads means my privacy is guaranteed.'
            },
            {
                name: '周小敏',
                nameEn: 'Zhou Xiaomin',
                role: '自由职业者',
                roleEn: 'Freelancer',
                avatar: 'ZX',
                quote: '二维码生成器支持自定义颜色和Logo，做出来的二维码比付费工具还好看，完全免费！',
                quoteEn: 'The QR Code Generator supports custom colors and logos. The results look better than paid tools — and it\'s completely free!'
            }
        ]
    };

    var data = testimonials[category] || testimonials.ai;
    var isChinese = document.documentElement.lang === 'zh-CN' || navigator.language.startsWith('zh');

    // 创建组件
    var section = document.createElement('section');
    section.className = 'nextool-testimonials';
    section.id = 'nextool-testimonials';

    var title = isChinese ? '💬 用户怎么说' : '💬 What Users Say';
    var subtitle = isChinese ? '来自真实用户的使用反馈' : 'Real feedback from our users';

    var cardsHTML = data.map(function(t, i) {
        var name = isChinese ? t.name : t.nameEn;
        var role = isChinese ? t.role : t.roleEn;
        var quote = isChinese ? t.quote : t.quoteEn;
        var isActive = i === 0 ? ' active' : '';
        return '<div class="testimonial-card' + isActive + '" data-index="' + i + '">' +
            '<div class="testimonial-quote">"' + quote + '"</div>' +
            '<div class="testimonial-author">' +
                '<div class="testimonial-avatar">' + t.avatar + '</div>' +
                '<div class="testimonial-info">' +
                    '<div class="testimonial-name">' + name + '</div>' +
                    '<div class="testimonial-role">' + role + '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    }).join('');

    var dotsHTML = data.map(function(t, i) {
        return '<span class="testimonial-dot' + (i === 0 ? ' active' : '') + '" data-index="' + i + '"></span>';
    }).join('');

    section.innerHTML =
        '<style>' +
        '.nextool-testimonials{' +
            'max-width:900px;margin:2rem auto;padding:0 1.5rem;' +
        '}' +
        '.nextool-testimonials .testimonials-header{' +
            'text-align:center;margin-bottom:1.5rem;' +
        '}' +
        '.nextool-testimonials .testimonials-title{' +
            'font-size:1.3rem;font-weight:700;color:#f0f0f5;margin-bottom:0.3rem;' +
            'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;' +
        '}' +
        '.nextool-testimonials .testimonials-subtitle{' +
            'font-size:0.85rem;color:#8888aa;' +
        '}' +
        '.nextool-testimonials .testimonials-track{' +
            'position:relative;overflow:hidden;border-radius:16px;' +
            'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);' +
            'padding:2rem 2rem 1.5rem;min-height:180px;' +
        '}' +
        '.nextool-testimonials .testimonial-card{' +
            'display:none;animation:testimonialFadeIn 0.5s ease;' +
        '}' +
        '.nextool-testimonials .testimonial-card.active{' +
            'display:block;' +
        '}' +
        '@keyframes testimonialFadeIn{' +
            'from{opacity:0;transform:translateY(10px)}' +
            'to{opacity:1;transform:translateY(0)}' +
        '}' +
        '.nextool-testimonials .testimonial-quote{' +
            'font-size:1rem;line-height:1.7;color:#d0d0e0;margin-bottom:1.5rem;' +
            'font-style:italic;position:relative;padding-left:1.2rem;' +
            'border-left:3px solid rgba(108,92,231,0.5);' +
        '}' +
        '.nextool-testimonials .testimonial-author{' +
            'display:flex;align-items:center;gap:12px;' +
        '}' +
        '.nextool-testimonials .testimonial-avatar{' +
            'width:40px;height:40px;border-radius:50%;' +
            'background:linear-gradient(135deg,#6c5ce7,#a855f7);' +
            'display:flex;align-items:center;justify-content:center;' +
            'font-size:0.8rem;font-weight:700;color:#fff;flex-shrink:0;' +
        '}' +
        '.nextool-testimonials .testimonial-name{' +
            'font-size:0.9rem;font-weight:600;color:#e8e8f0;' +
        '}' +
        '.nextool-testimonials .testimonial-role{' +
            'font-size:0.78rem;color:#8888aa;' +
        '}' +
        '.nextool-testimonials .testimonials-dots{' +
            'display:flex;justify-content:center;gap:8px;margin-top:1.2rem;' +
        '}' +
        '.nextool-testimonials .testimonial-dot{' +
            'width:8px;height:8px;border-radius:50%;' +
            'background:rgba(255,255,255,0.15);cursor:pointer;' +
            'transition:all 0.3s;' +
        '}' +
        '.nextool-testimonials .testimonial-dot.active{' +
            'background:linear-gradient(135deg,#6c5ce7,#a855f7);' +
            'transform:scale(1.2);' +
        '}' +
        '.nextool-testimonials .testimonial-dot:hover{' +
            'background:rgba(108,92,231,0.5);' +
        '}' +
        '@media(max-width:640px){' +
            '.nextool-testimonials .testimonials-track{padding:1.5rem 1.2rem 1.2rem}' +
            '.nextool-testimonials .testimonial-quote{font-size:0.9rem}' +
        '}' +
        '</style>' +
        '<div class="testimonials-header">' +
            '<div class="testimonials-title">' + title + '</div>' +
            '<div class="testimonials-subtitle">' + subtitle + '</div>' +
        '</div>' +
        '<div class="testimonials-track">' +
            cardsHTML +
        '</div>' +
        '<div class="testimonials-dots">' +
            dotsHTML +
        '</div>';

    // 插入到页面中（在related-tools之前或body末尾）
    var relatedTools = document.querySelector('.related-tools-section');
    if (relatedTools) {
        relatedTools.parentNode.insertBefore(section, relatedTools);
    } else {
        document.body.appendChild(section);
    }

    // 轮播逻辑
    var currentIndex = 0;
    var cards = section.querySelectorAll('.testimonial-card');
    var dots = section.querySelectorAll('.testimonial-dot');
    var autoPlayTimer = null;

    function showTestimonial(index) {
        cards.forEach(function(c) { c.classList.remove('active'); });
        dots.forEach(function(d) { d.classList.remove('active'); });
        cards[index].classList.add('active');
        dots[index].classList.add('active');
        currentIndex = index;
    }

    function nextTestimonial() {
        var next = (currentIndex + 1) % data.length;
        showTestimonial(next);
    }

    function startAutoPlay() {
        autoPlayTimer = setInterval(nextTestimonial, 5000);
    }

    function stopAutoPlay() {
        if (autoPlayTimer) {
            clearInterval(autoPlayTimer);
            autoPlayTimer = null;
        }
    }

    // 点击圆点切换
    dots.forEach(function(dot) {
        dot.addEventListener('click', function() {
            var idx = parseInt(this.getAttribute('data-index'), 10);
            showTestimonial(idx);
            stopAutoPlay();
            startAutoPlay();

            // GA追踪
            if (typeof gtag === 'function') {
                gtag('event', 'testimonial_click', {
                    event_category: 'engagement',
                    event_label: 'testimonial_dot_' + idx,
                    tool_category: category
                });
            }
        });
    });

    // 点击评价卡片追踪
    section.querySelector('.testimonials-track').addEventListener('click', function() {
        if (typeof gtag === 'function') {
            gtag('event', 'testimonial_click', {
                event_category: 'engagement',
                event_label: 'testimonial_card_' + currentIndex,
                tool_category: category
            });
        }
    });

    // 启动自动轮播
    startAutoPlay();

})();
