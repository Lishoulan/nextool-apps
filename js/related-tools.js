/**
 * NextTool Related Tools - 工具内链系统
 * 在每个工具页面底部显示相关工具，提升SEO内链权重
 * 
 * 使用方法：
 * <script src="../js/related-tools.js" data-current="ai-ppt-generator"></script>
 */

(function() {
    'use strict';

    const tools = {
        'ai-ppt-generator': {
            name: 'AI PPT生成器',
            icon: '📊',
            url: '../ai-ppt-generator/',
            desc: '60秒生成专业PPT',
            category: 'ai',
            related: ['ai-resume-optimizer', 'ai-contract-generator', 'ai-email-writer', 'pdf-toolkit', 'word-counter']
        },
        'ai-resume-optimizer': {
            name: 'AI简历优化器',
            icon: '📄',
            url: '../ai-resume-optimizer/',
            desc: 'HR一眼看上的简历',
            category: 'ai',
            related: ['ai-ppt-generator', 'ai-email-writer', 'ai-paper-rewriter', 'word-counter', 'qr-generator']
        },
        'ai-contract-generator': {
            name: 'AI合同生成器',
            icon: '📋',
            url: '../ai-contract-generator/',
            desc: '12种专业合同模板',
            category: 'ai',
            related: ['ai-email-writer', 'ai-paper-rewriter', 'pdf-toolkit', 'ai-translator', 'ai-resume-optimizer']
        },
        'ai-email-writer': {
            name: 'AI邮件写作器',
            icon: '✉️',
            url: '../ai-email-writer/',
            desc: '10种商务邮件场景',
            category: 'ai',
            related: ['ai-translator', 'ai-resume-optimizer', 'ai-contract-generator', 'ai-paper-rewriter', 'ai-ppt-generator']
        },
        'ai-paper-rewriter': {
            name: 'AI论文降重',
            icon: '📝',
            url: '../ai-paper-rewriter/',
            desc: '智能改写降低查重率',
            category: 'ai',
            related: ['ai-translator', 'ai-summarizer', 'word-counter', 'ai-resume-optimizer', 'ai-code-explainer']
        },
        'ai-translator': {
            name: 'AI翻译工具',
            icon: '🌐',
            url: '../ai-translator/',
            desc: '8种语言互译',
            category: 'ai',
            related: ['ai-email-writer', 'ai-paper-rewriter', 'ai-code-explainer', 'ai-summarizer', 'ai-resume-optimizer']
        },
        'ai-code-explainer': {
            name: 'AI代码解释器',
            icon: '💻',
            url: '../ai-code-explainer/',
            desc: '逐行解释代码逻辑',
            category: 'ai',
            related: ['json-formatter', 'regex-tester', 'base64-tool', 'url-tool', 'markdown-editor']
        },
        'ai-summarizer': {
            name: 'AI文本摘要',
            icon: '📑',
            url: '../ai-summarizer/',
            desc: '免费TextRank摘要',
            category: 'ai',
            related: ['ai-paper-rewriter', 'ai-translator', 'word-counter', 'pdf-toolkit', 'ai-email-writer']
        },
        'pdf-toolkit': {
            name: 'PDF工具箱',
            icon: '📕',
            url: '../pdf-toolkit/',
            desc: '6大PDF功能免费使用',
            category: 'free',
            related: ['image-compressor', 'word-counter', 'qr-generator', 'ai-summarizer', 'base64-tool']
        },
        'json-formatter': {
            name: 'JSON格式化',
            icon: '🔧',
            url: '../json-formatter/',
            desc: 'JSON美化压缩验证',
            category: 'free',
            related: ['regex-tester', 'base64-tool', 'url-tool', 'ai-code-explainer', 'markdown-editor']
        },
        'qr-generator': {
            name: '二维码生成器',
            icon: '📱',
            url: '../qr-generator/',
            desc: '免费生成二维码',
            category: 'free',
            related: ['password-generator', 'image-compressor', 'pdf-toolkit', 'color-picker', 'base64-tool']
        },
        'regex-tester': {
            name: '正则测试器',
            icon: '🔍',
            url: '../regex-tester/',
            desc: '正则表达式在线测试',
            category: 'free',
            related: ['json-formatter', 'ai-code-explainer', 'base64-tool', 'url-tool', 'markdown-editor']
        },
        'color-picker': {
            name: '颜色选择器',
            icon: '🎨',
            url: '../color-picker/',
            desc: 'HEX/RGB/HSL转换',
            category: 'free',
            related: ['qr-generator', 'image-compressor', 'markdown-editor', 'base64-tool', 'url-tool']
        },
        'markdown-editor': {
            name: 'Markdown编辑器',
            icon: '✏️',
            url: '../markdown-editor/',
            desc: '实时预览Markdown',
            category: 'free',
            related: ['json-formatter', 'word-counter', 'ai-code-explainer', 'regex-tester', 'color-picker']
        },
        'base64-tool': {
            name: 'Base64编解码',
            icon: '🔐',
            url: '../base64-tool/',
            desc: 'Base64编码解码',
            category: 'free',
            related: ['url-tool', 'json-formatter', 'ai-code-explainer', 'regex-tester', 'password-generator']
        },
        'url-tool': {
            name: 'URL编解码',
            icon: '🔗',
            url: '../url-tool/',
            desc: 'URL编码解码转换',
            category: 'free',
            related: ['base64-tool', 'json-formatter', 'ai-code-explainer', 'regex-tester', 'qr-generator']
        },
        'timestamp-tool': {
            name: '时间戳转换',
            icon: '⏰',
            url: '../timestamp-tool/',
            desc: 'Unix时间戳转换',
            category: 'free',
            related: ['calculator', 'color-picker', 'qr-generator', 'word-counter', 'password-generator']
        },
        'password-generator': {
            name: '密码生成器',
            icon: '🔑',
            url: '../password-generator/',
            desc: '强密码生成+强度检测',
            category: 'free',
            related: ['base64-tool', 'qr-generator', 'url-tool', 'timestamp-tool', 'json-formatter']
        },
        'word-counter': {
            name: '字数统计',
            icon: '📊',
            url: '../word-counter/',
            desc: '中英文词频分析',
            category: 'free',
            related: ['ai-summarizer', 'ai-paper-rewriter', 'markdown-editor', 'pdf-toolkit', 'ai-translator']
        },
        'image-compressor': {
            name: '图片压缩',
            icon: '🖼️',
            url: '../image-compressor/',
            desc: '批量压缩JPG/PNG/WebP',
            category: 'free',
            related: ['pdf-toolkit', 'qr-generator', 'color-picker', 'calculator', 'word-counter']
        },
        'calculator': {
            name: '在线计算器',
            icon: '🧮',
            url: '../calculator/',
            desc: '科学计算+单位换算',
            category: 'free',
            related: ['timestamp-tool', 'password-generator', 'word-counter', 'image-compressor', 'color-picker']
        }
    };

    const currentSlug = document.currentScript ? 
        document.currentScript.getAttribute('data-current') : null;

    if (!currentSlug || !tools[currentSlug]) return;

    const currentTool = tools[currentSlug];
    const relatedSlugs = currentTool.related || [];

    // 创建内链区域
    const section = document.createElement('section');
    section.className = 'related-tools-section';
    section.innerHTML = `
        <style>
            .related-tools-section {
                margin: 3rem auto 0;
                padding: 2rem;
                max-width: 900px;
                border-top: 1px solid rgba(255,255,255,0.08);
            }
            .related-tools-section h3 {
                color: #f0f0f5;
                font-size: 1.3rem;
                margin-bottom: 1.2rem;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }
            .related-tools-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
                gap: 12px;
            }
            .related-tool-card {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 14px;
                border-radius: 12px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.06);
                text-decoration: none;
                color: #f0f0f5;
                transition: all 0.25s ease;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            }
            .related-tool-card:hover {
                background: rgba(240,185,11,0.08);
                border-color: rgba(240,185,11,0.25);
                transform: translateY(-2px);
            }
            .related-tool-card .tool-icon {
                font-size: 1.5rem;
                line-height: 1;
                flex-shrink: 0;
            }
            .related-tool-card .tool-info {
                min-width: 0;
            }
            .related-tool-card .tool-name {
                font-size: 0.9rem;
                font-weight: 600;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .related-tool-card .tool-desc {
                font-size: 0.75rem;
                color: #a0a0b8;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .related-tool-card .tool-badge {
                font-size: 0.6rem;
                padding: 2px 6px;
                border-radius: 4px;
                background: rgba(240,185,11,0.15);
                color: #f0b90b;
                font-weight: 600;
                flex-shrink: 0;
            }
            .related-tool-card .tool-badge.free {
                background: rgba(0,212,170,0.15);
                color: #00d4aa;
            }
            @media (max-width: 640px) {
                .related-tools-grid {
                    grid-template-columns: 1fr 1fr;
                }
                .related-tool-card {
                    padding: 10px 12px;
                }
            }
        </style>
        <h3>🔧 相关工具推荐</h3>
        <div class="related-tools-grid">
            ${relatedSlugs.map(slug => {
                const t = tools[slug];
                if (!t) return '';
                const badgeClass = t.category === 'free' ? 'free' : '';
                const badgeText = t.category === 'free' ? '免费' : 'AI';
                return `<a href="${t.url}" class="related-tool-card">
                    <span class="tool-icon">${t.icon}</span>
                    <div class="tool-info">
                        <div class="tool-name">${t.name}</div>
                        <div class="tool-desc">${t.desc}</div>
                    </div>
                    <span class="tool-badge ${badgeClass}">${badgeText}</span>
                </a>`;
            }).join('')}
        </div>
    `;

    // 插入到页面底部
    const mainContent = document.querySelector('main') || document.querySelector('.container') || document.body;
    mainContent.appendChild(section);

    // GA追踪
    section.addEventListener('click', function(e) {
        const card = e.target.closest('.related-tool-card');
        if (card && typeof gtag === 'function') {
            gtag('event', 'related_tool_click', {
                from: currentSlug,
                to: card.href
            });
        }
    });
})();
