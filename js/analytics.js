/**
 * NextTool Google Analytics 跟踪脚本
 * 提供页面视图、工具使用和转化事件的跟踪功能
 */

// 工具配置映射
const TOOL_CONFIG = {
  // AI 工具
  'ai-code-explainer': {
    name: 'AI 代码解释器',
    category: 'AI Tools',
    events: {
      explain: { action: 'explain_code', label: '解释代码' },
      optimize: { action: 'optimize_code', label: '优化代码' },
      generate: { action: 'generate_code', label: '生成代码' }
    }
  },
  'ai-contract-generator': {
    name: 'AI 合同生成器',
    category: 'AI Tools',
    events: {
      generate: { action: 'generate_contract', label: '生成合同' },
      download: { action: 'download_contract', label: '下载合同' }
    }
  },
  'ai-email-writer': {
    name: 'AI 邮件写作器',
    category: 'AI Tools',
    events: {
      generate: { action: 'generate_email', label: '生成邮件' },
      rewrite: { action: 'rewrite_email', label: '重写邮件' }
    }
  },
  'ai-paper-rewriter': {
    name: '论文降重助手',
    category: 'AI Tools',
    events: {
      rewrite: { action: 'rewrite_paper', label: '改写论文' },
      paraphrase: { action: 'paraphrase', label: '复述' }
    }
  },
  'ai-ppt-generator': {
    name: 'AI PPT 生成器',
    category: 'AI Tools',
    events: {
      generate: { action: 'generate_ppt', label: '生成 PPT' },
      download: { action: 'download_ppt', label: '下载 PPT' }
    }
  },
  'ai-resume-optimizer': {
    name: 'AI 简历优化器',
    category: 'AI Tools',
    events: {
      optimize: { action: 'optimize_resume', label: '优化简历' },
      generate: { action: 'generate_resume', label: '生成简历' }
    }
  },
  'ai-summarizer': {
    name: 'AI 文本摘要',
    category: 'AI Tools',
    events: {
      summarize: { action: 'summarize_text', label: '摘要文本' }
    }
  },
  'ai-translator': {
    name: 'AI 翻译工具',
    category: 'AI Tools',
    events: {
      translate: { action: 'translate_text', label: '翻译文本' }
    }
  },
  
  // 免费工具
  'base64-tool': {
    name: 'Base64 编解码器',
    category: 'Free Tools',
    events: {
      encode: { action: 'encode_base64', label: 'Base64 编码' },
      decode: { action: 'decode_base64', label: 'Base64 解码' }
    }
  },
  'color-picker': {
    name: '颜色选择器',
    category: 'Free Tools',
    events: {
      pick: { action: 'pick_color', label: '选择颜色' },
      convert: { action: 'convert_color', label: '转换颜色格式' }
    }
  },
  'json-formatter': {
    name: 'JSON 格式化',
    category: 'Free Tools',
    events: {
      format: { action: 'format_json', label: '格式化 JSON' },
      validate: { action: 'validate_json', label: '验证 JSON' }
    }
  },
  'markdown-editor': {
    name: 'Markdown 编辑器',
    category: 'Free Tools',
    events: {
      edit: { action: 'edit_markdown', label: '编辑 Markdown' },
      preview: { action: 'preview_markdown', label: '预览 Markdown' },
      export: { action: 'export_markdown', label: '导出 HTML' }
    }
  },
  'pdf-toolkit': {
    name: 'PDF 工具箱',
    category: 'Free Tools',
    events: {
      merge: { action: 'merge_pdf', label: '合并 PDF' },
      split: { action: 'split_pdf', label: '拆分 PDF' },
      convert: { action: 'pdf_to_image', label: 'PDF 转图片' },
      image_to_pdf: { action: 'image_to_pdf', label: '图片转 PDF' },
      compress: { action: 'compress_pdf', label: '压缩 PDF' },
      watermark: { action: 'add_watermark', label: '添加水印' }
    }
  },
  'qr-generator': {
    name: '二维码生成器',
    category: 'Free Tools',
    events: {
      generate: { action: 'generate_qr', label: '生成二维码' },
      download: { action: 'download_qr', label: '下载二维码' }
    }
  },
  'regex-tester': {
    name: '正则测试器',
    category: 'Free Tools',
    events: {
      test: { action: 'test_regex', label: '测试正则表达式' }
    }
  },
  'timestamp-tool': {
    name: '时间戳转换',
    category: 'Free Tools',
    events: {
      convert: { action: 'convert_timestamp', label: '转换时间戳' }
    }
  },
  'url-tool': {
    name: 'URL 编解码器',
    category: 'Free Tools',
    events: {
      encode: { action: 'encode_url', label: 'URL 编码' },
      decode: { action: 'decode_url', label: 'URL 解码' }
    }
  },
  'password-generator': {
    name: '密码生成器',
    category: 'Free Tools',
    events: {
      generate: { action: 'generate_password', label: '生成密码' },
      copy: { action: 'copy_password', label: '复制密码' }
    }
  },
  'word-counter': {
    name: '字数统计',
    category: 'Free Tools',
    events: {
      count: { action: 'count_words', label: '统计字数' }
    }
  },
  'image-compressor': {
    name: '图片压缩',
    category: 'Free Tools',
    events: {
      compress: { action: 'compress_image', label: '压缩图片' },
      download: { action: 'download_compressed', label: '下载压缩图片' }
    }
  },
  'calculator': {
    name: '在线计算器',
    category: 'Free Tools',
    events: {
      calculate: { action: 'calculate', label: '计算' }
    }
  },
  
  // 其他页面
  'chrome-extension': {
    name: 'Chrome 扩展',
    category: 'Resources',
    events: {
      install: { action: 'install_extension', label: '安装扩展' }
    }
  },
  'pay': {
    name: '支付页面',
    category: 'Conversion',
    events: {
      select_plan: { action: 'select_plan', label: '选择套餐' },
      generate_code: { action: 'generate_code', label: '生成兑换码' },
      copy_code: { action: 'copy_code', label: '复制兑换码' }
    }
  },
  'tools': {
    name: '工具目录',
    category: 'Resources',
    events: {
      click_tool: { action: 'click_tool', label: '点击工具' }
    }
  },
  'pricing': {
    name: '定价方案',
    category: 'Conversion',
    events: {
      view_plan: { action: 'view_plan', label: '查看套餐' }
    }
  }
};

// 当前页面工具信息
let currentTool = null;

// 初始化 GA
function initGA() {
  if (!window.dataLayer) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){window.dataLayer.push(arguments);};
    window.gtag('js', new Date());
  }
}

// 初始化页面跟踪
function initPageTracking(toolId) {
  initGA();
  
  if (TOOL_CONFIG[toolId]) {
    currentTool = TOOL_CONFIG[toolId];
  } else {
    // 从 URL 路径推断工具 ID
    const path = window.location.pathname;
    const matches = path.match(/\/([^\/]+)\/?$/);
    if (matches && TOOL_CONFIG[matches[1]]) {
      currentTool = TOOL_CONFIG[matches[1]];
    }
  }
  
  // 发送页面视图事件
  if (currentTool) {
    gtag('config', 'G-H0PJ9V418V', {
      'page_title': currentTool.name,
      'page_category': currentTool.category
    });
  } else {
    gtag('config', 'G-H0PJ9V418V');
  }
}

// 跟踪工具使用事件
function trackToolEvent(eventKey, params = {}) {
  if (!currentTool) return;
  
  const event = currentTool.events[eventKey];
  if (!event) return;
  
  gtag('event', event.action, {
    'event_category': currentTool.category,
    'event_label': event.label,
    ...params
  });
}

// 跟踪自定义事件
function trackEvent(action, category, label, params = {}) {
  gtag('event', action, {
    'event_category': category,
    'event_label': label,
    ...params
  });
}

// 跟踪页面视图（用于 SPA 导航）
function trackPageView(pagePath, pageTitle) {
  gtag('config', 'G-H0PJ9V418V', {
    'page_path': pagePath,
    'page_title': pageTitle
  });
}

// 暴露到全局
window.NextToolAnalytics = {
  initGA,
  initPageTracking,
  trackToolEvent,
  trackEvent,
  trackPageView,
  TOOL_CONFIG
};
