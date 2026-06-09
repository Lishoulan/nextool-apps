#!/usr/bin/env python3
"""
Daily SEO content generator for NextTool.
Uses DeepSeek API to generate SEO-optimized Chinese blog articles.
Creates HTML files in the blog/ directory.
"""

import json
import os
import re
import random
import requests
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
BASE_URL = "https://lishoulan.github.io/nextool-apps"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Predefined topic list (10 topics)
TOPICS = [
    {
        "title": "免费AI写作工具推荐",
        "keywords": "AI写作工具,免费AI写作,在线写作助手,AI文案生成,写作工具推荐",
        "slug": "free-ai-writing-tools",
        "tool": "ai-email-writer",
    },
    {
        "title": "AI论文降重方法大全",
        "keywords": "AI论文降重,论文降重方法,查重降重,学术写作,论文修改",
        "slug": "ai-paper-rewriting-methods",
        "tool": "ai-paper-rewriter",
    },
    {
        "title": "在线PDF工具哪个好用",
        "keywords": "在线PDF工具,PDF合并,PDF压缩,免费PDF,PDF处理",
        "slug": "best-online-pdf-tools",
        "tool": "pdf-toolkit",
    },
    {
        "title": "免费AI翻译工具对比",
        "keywords": "AI翻译工具,免费翻译,在线翻译,翻译对比,多语言翻译",
        "slug": "free-ai-translation-tools-comparison",
        "tool": "ai-translator",
    },
    {
        "title": "程序员必备在线工具",
        "keywords": "程序员工具,在线开发工具,JSON格式化,正则测试,编码解码",
        "slug": "must-have-online-tools-for-developers",
        "tool": "json-formatter",
    },
    {
        "title": "AI简历优化技巧",
        "keywords": "AI简历优化,简历写作技巧,求职简历,面试准备,简历模板",
        "slug": "ai-resume-optimization-tips",
        "tool": "ai-resume-optimizer",
    },
    {
        "title": "免费AI PPT生成器",
        "keywords": "AI PPT生成器,免费PPT制作,演示文稿生成,在线PPT,AI办公",
        "slug": "free-ai-ppt-generator",
        "tool": "ai-ppt-generator",
    },
    {
        "title": "AI合同生成器使用指南",
        "keywords": "AI合同生成器,合同模板,法律文书,在线合同,免费合同",
        "slug": "ai-contract-generator-guide",
        "tool": "ai-contract-generator",
    },
    {
        "title": "学生党免费工具推荐",
        "keywords": "学生免费工具,学习工具,学生必备,在线工具,效率工具",
        "slug": "free-tools-for-students",
        "tool": "ai-paper-rewriter",
    },
    {
        "title": "打工人效率提升工具",
        "keywords": "效率提升工具,办公效率,打工人必备,在线工具,职场工具",
        "slug": "productivity-tools-for-workers",
        "tool": "ai-email-writer",
    },
]


def select_topic():
    """Randomly select a topic from the predefined list."""
    topic = random.choice(TOPICS)
    print(f"📋 Selected topic: {topic['title']}")
    return topic


def generate_article(topic):
    """Use DeepSeek API to generate a Chinese SEO blog article."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")

    prompt = f"""你是一位专业的中文SEO博客写手，为NexTool（一个在线AI效率工具平台）撰写SEO优化的博客文章。

请根据以下主题写一篇博客文章：
- 标题：{topic['title']}
- 关键词：{topic['keywords']}
- 关联工具：{topic['tool']}（工具链接：{BASE_URL}/{topic['tool']}/）

要求：
1. 文章长度800-1500字
2. 包含引言、3-4个正文章节（每个章节有h2标题）、FAQ和总结
3. 自然地融入关键词，不堆砌
4. 在文章中至少2处自然地提及NexTool平台并附上链接 {BASE_URL}/
5. 语气专业但亲切，像朋友间分享经验
6. 包含具体的操作步骤和实用建议
7. FAQ部分包含3-5个常见问题

请用以下JSON格式返回：
{{
  "title": "文章标题",
  "description": "文章描述（150字以内，用于meta description）",
  "keywords": "关键词1,关键词2,关键词3",
  "content_html": "文章正文的HTML内容（h2, h3, p, ul, ol, blockquote标签）",
  "faq_html": "FAQ部分的HTML内容（h3标题+段落）",
  "conclusion_html": "总结部分的HTML内容"
}}"""

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的中文技术博客写手，擅长撰写SEO优化的实用指南类文章。输出必须是纯JSON格式，不要包含markdown代码块标记。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()

    # Remove markdown code block markers if present
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    try:
        article = json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse API response as JSON, attempting extraction...")
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            article = json.loads(json_match.group())
        else:
            raise ValueError("Could not extract JSON from API response")

    return article


def create_slug_from_title(title):
    """Create a URL-friendly slug from Chinese title."""
    # Simple transliteration mapping for common Chinese characters in topics
    slug_map = {
        "免费AI写作工具推荐": "free-ai-writing-tools",
        "AI论文降重方法大全": "ai-paper-rewriting-methods",
        "在线PDF工具哪个好用": "best-online-pdf-tools",
        "免费AI翻译工具对比": "free-ai-translation-tools-comparison",
        "程序员必备在线工具": "must-have-online-tools-for-developers",
        "AI简历优化技巧": "ai-resume-optimization-tips",
        "免费AI PPT生成器": "free-ai-ppt-generator",
        "AI合同生成器使用指南": "ai-contract-generator-guide",
        "学生党免费工具推荐": "free-tools-for-students",
        "打工人效率提升工具": "productivity-tools-for-workers",
    }
    return slug_map.get(title, re.sub(r'[^\w\s-]', '', title.lower()).replace(' ', '-'))


def create_blog_html(article, topic):
    """Create a complete HTML blog article file with dark theme and gradient titles."""
    slug = topic["slug"]
    filename = f"{TODAY}-{slug}.html"
    filepath = os.path.join(BLOG_DIR, filename)
    url = f"{BASE_URL}/blog/{filename}"

    title = article.get("title", topic["title"])
    description = article.get("description", "")
    keywords = article.get("keywords", topic["keywords"])
    content_html = article.get("content_html", "")
    faq_html = article.get("faq_html", "")
    conclusion_html = article.get("conclusion_html", "")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | NexTool博客</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="NexTool">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="NexTool">
<meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{description}",
  "keywords": "{keywords}",
  "author": {{"@type": "Organization", "name": "NexTool"}},
  "publisher": {{
    "@type": "Organization",
    "name": "NexTool",
    "logo": {{
      "@type": "ImageObject",
      "url": "{BASE_URL}/icons/icon-192x192.png"
    }}
  }},
  "datePublished": "{TODAY}",
  "dateModified": "{TODAY}",
  "mainEntityOfPage": "{url}"
}}
</script>
<link rel="stylesheet" href="../css/mobile.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#0a0a0f;--bg2:#1a1a2e;--accent:#6c5ce7;--accent2:#a855f7;--accent3:#06b6d4;--text:#e8e8f0;--text-dim:#8888aa;--card-bg:rgba(255,255,255,0.06);--card-border:rgba(255,255,255,0.1);--radius:12px}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:linear-gradient(135deg,var(--bg),var(--bg2),#12121a);color:var(--text);line-height:1.8;min-height:100vh}}
.nav{{position:sticky;top:0;z-index:100;backdrop-filter:blur(20px);background:rgba(10,10,15,0.8);border-bottom:1px solid var(--card-border);padding:14px 24px;display:flex;align-items:center;justify-content:space-between}}
.nav-logo{{font-size:1.2rem;font-weight:700;background:linear-gradient(135deg,var(--accent2),var(--accent3));-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-decoration:none}}
.nav-links{{display:flex;gap:20px;list-style:none}}
.nav-links a{{color:var(--text-dim);text-decoration:none;font-size:.9rem;transition:color .3s}}
.nav-links a:hover{{color:#fff}}
.layout{{max-width:1100px;margin:0 auto;padding:32px 20px;display:grid;grid-template-columns:1fr 280px;gap:32px}}
@media(max-width:768px){{.layout{{grid-template-columns:1fr}}}}
.article h1{{font-size:2rem;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,var(--accent2),var(--accent3));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.article .meta{{color:var(--text-dim);font-size:.85rem;margin-bottom:28px;padding-bottom:16px;border-bottom:1px solid var(--card-border)}}
.article h2{{font-size:1.4rem;font-weight:700;margin:32px 0 16px;color:#fff}}
.article h3{{font-size:1.15rem;font-weight:600;margin:24px 0 12px;color:var(--accent2)}}
.article p{{margin-bottom:16px;color:var(--text)}}
.article ul,.article ol{{margin:12px 0 16px 24px;color:var(--text)}}
.article li{{margin-bottom:8px}}
.article blockquote{{border-left:3px solid var(--accent2);padding:12px 20px;margin:20px 0;background:var(--card-bg);border-radius:0 var(--radius) var(--radius) 0;color:var(--text-dim)}}
.article a{{color:var(--accent3);text-decoration:none}}
.article a:hover{{text-decoration:underline}}
.cta-btn{{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-radius:50px;text-decoration:none;font-weight:600;font-size:1rem;transition:transform .3s,box-shadow .3s;margin:20px 0}}
.cta-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 25px rgba(168,85,247,0.4);text-decoration:none}}
.sidebar-card{{background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--radius);padding:20px;margin-bottom:20px;backdrop-filter:blur(10px)}}
.sidebar-card h3{{font-size:1rem;font-weight:700;margin-bottom:14px;color:var(--accent2)}}
.sidebar-card ul{{list-style:none}}
.sidebar-card li{{margin-bottom:10px}}
.sidebar-card a{{color:var(--text-dim);text-decoration:none;font-size:.9rem;transition:color .3s;display:flex;align-items:center;gap:6px}}
.sidebar-card a:hover{{color:var(--accent2)}}
footer{{text-align:center;padding:32px;color:var(--text-dim);font-size:.8rem;border-top:1px solid var(--card-border);margin-top:40px}}
footer a{{color:var(--accent2);text-decoration:none}}
</style>
</head>
<body>
<nav class="nav">
  <a href="{BASE_URL}/" class="nav-logo">⚡ NexTool</a>
  <ul class="nav-links">
    <li><a href="{BASE_URL}/">首页</a></li>
    <li><a href="{BASE_URL}/blog/">博客</a></li>
    <li><a href="{BASE_URL}/{topic['tool']}/">工具</a></li>
  </ul>
</nav>
<div class="layout">
  <main class="article">
    <h1>{title}</h1>
    <div class="meta">📅 {TODAY} · 📖 阅读约6分钟 · 🏷️ {keywords.split(',')[0]}</div>
    {content_html}
    <h2>常见问题</h2>
    {faq_html}
    <h2>总结</h2>
    {conclusion_html}
    <div style="text-align:center;margin:32px 0">
      <a href="{BASE_URL}/{topic['tool']}/" class="cta-btn">🚀 立即体验{keywords.split(',')[0]}工具</a>
    </div>
  </main>
  <aside>
    <div class="sidebar-card">
      <h3>🔥 热门工具</h3>
      <ul>
        <li><a href="{BASE_URL}/ai-ppt-generator/">AI PPT生成器</a></li>
        <li><a href="{BASE_URL}/ai-resume-optimizer/">AI简历优化</a></li>
        <li><a href="{BASE_URL}/ai-email-writer/">AI邮件写作</a></li>
        <li><a href="{BASE_URL}/pdf-toolkit/">PDF工具箱</a></li>
        <li><a href="{BASE_URL}/json-formatter/">JSON格式化</a></li>
      </ul>
    </div>
    <div class="sidebar-card">
      <h3>📝 最新文章</h3>
      <ul>
        <li><a href="{BASE_URL}/blog/">查看所有文章 →</a></li>
      </ul>
    </div>
  </aside>
</div>
<footer>
  <p>© {datetime.now().year} NexTool · <a href="{BASE_URL}/">在线AI效率工具平台</a></p>
</footer>
<script>
(function(){{
  var bp = document.createElement('script');
  var curProtocol = window.location.protocol.split(':')[0];
  if (curProtocol === 'https') {{
    bp.src = 'https://zz.bdstatic.com/linksubmit/push.js';
  }} else {{
    bp.src = 'http://push.zhanzhang.baidu.com/push.js';
  }}
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(bp, s);
}})();
</script>
</body>
</html>"""

    os.makedirs(BLOG_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Blog article created: {filepath}")
    print(f"   URL: {url}")
    return filename


def main():
    print(f"🤖 Daily SEO Content Generator - {TODAY}")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not set.")
        raise SystemExit(1)

    topic = select_topic()

    try:
        article = generate_article(topic)
        filename = create_blog_html(article, topic)
        print(f"🎉 Successfully generated blog article: {filename}")
    except Exception as e:
        print(f"❌ Failed to generate article: {e}")
        raise


if __name__ == "__main__":
    main()
