#!/usr/bin/env python3
"""
Daily blog article generator for NextTool.
Uses DeepSeek API to generate SEO-optimized blog articles.
Creates HTML files in the blog/ directory.
"""

import json
import os
import re
import random
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
BASE_URL = "https://lishoulan.github.io/nextool-apps"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Topics pool - SEO keywords related to NextTool's tools
TOPICS = [
    {"title": "AI工具如何帮助自由职业者提高收入", "keywords": "AI工具,自由职业,提高收入,效率工具", "tool": "ai-summarizer"},
    {"title": "2025年最值得尝试的在线JSON格式化工具", "keywords": "JSON格式化,在线工具,开发者工具,JSON校验", "tool": "json-formatter"},
    {"title": "如何用AI快速生成专业商务合同", "keywords": "AI合同生成,商务合同,法律文书,在线工具", "tool": "ai-contract-generator"},
    {"title": "在线密码生成器：如何创建安全的密码", "keywords": "密码生成器,安全密码,在线工具,密码管理", "tool": "password-generator"},
    {"title": "Markdown编辑器对比：哪个最适合技术写作", "keywords": "Markdown编辑器,技术写作,在线编辑器,Markdown语法", "tool": "markdown-editor"},
    {"title": "前端开发者必备的颜色选择工具推荐", "keywords": "颜色选择器,前端开发,CSS颜色,设计工具", "tool": "color-picker"},
    {"title": "正则表达式测试工具使用指南", "keywords": "正则表达式,在线测试,Regex工具,编程效率", "tool": "regex-tester"},
    {"title": "如何用AI优化简历获得更多面试机会", "keywords": "AI简历优化,求职技巧,简历写作,面试准备", "tool": "ai-resume-optimizer"},
    {"title": "在线图片压缩工具对比评测", "keywords": "图片压缩,在线工具,网页优化,图片处理", "tool": "image-compressor"},
    {"title": "Base64编码解码工具详解", "keywords": "Base64编码,在线解码,开发者工具,数据转换", "tool": "base64-tool"},
    {"title": "URL编码解码：开发者必知的基础知识", "keywords": "URL编码,URL解码,在线工具,Web开发", "tool": "url-tool"},
    {"title": "Unix时间戳转换工具使用教程", "keywords": "时间戳转换,Unix时间,开发者工具,日期处理", "tool": "timestamp-tool"},
    {"title": "在线字数统计工具对内容创作者的价值", "keywords": "字数统计,内容创作,写作工具,SEO优化", "tool": "word-counter"},
    {"title": "AI翻译工具对比：哪个翻译最准确", "keywords": "AI翻译,在线翻译,多语言翻译,翻译工具", "tool": "ai-translator"},
    {"title": "如何用AI快速生成PPT演示文稿", "keywords": "AI生成PPT,演示文稿,办公效率,PPT制作", "tool": "ai-ppt-generator"},
    {"title": "AI论文改写工具：学术写作的好帮手", "keywords": "AI改写,论文写作,学术工具,降重方法", "tool": "ai-paper-rewriter"},
    {"title": "在线科学计算器使用指南", "keywords": "科学计算器,在线工具,数学计算,学生工具", "tool": "calculator"},
    {"title": "QR码生成器：快速创建自定义二维码", "keywords": "二维码生成,QR码,在线工具,营销推广", "tool": "qr-generator"},
    {"title": "AI邮件写作助手：提升商务沟通效率", "keywords": "AI邮件写作,商务邮件,沟通效率,邮件模板", "tool": "ai-email-writer"},
    {"title": "AI代码解释器：编程学习的新方式", "keywords": "AI代码解释,编程学习,代码理解,开发者工具", "tool": "ai-code-explainer"},
    {"title": "免费在线PDF工具合集推荐", "keywords": "PDF工具,在线PDF,免费工具,文档处理", "tool": "pdf-toolkit"},
    {"title": "AI摘要工具：快速提取文章核心要点", "keywords": "AI摘要,文章总结,阅读效率,信息提取", "tool": "ai-summarizer"},
]


def get_existing_articles():
    """Get list of existing blog HTML files to avoid duplicates."""
    existing = set()
    if os.path.isdir(BLOG_DIR):
        for f in os.listdir(BLOG_DIR):
            if f.endswith(".html") and f != "index.html":
                existing.add(f)
    return existing


def select_topic():
    """Select a topic that hasn't been covered recently."""
    existing = get_existing_articles()
    # Filter out topics that already have articles
    available = []
    for topic in TOPICS:
        # Generate expected filename from title
        slug = re.sub(r'[^\w\s-]', '', topic["title"].lower())
        slug = re.sub(r'[\s]+', '-', slug)
        expected_file = f"{slug}.html"
        if expected_file not in existing:
            available.append(topic)

    if not available:
        # If all topics covered, pick a random one with a date suffix
        available = TOPICS

    return random.choice(available)


def generate_article(topic):
    """Use DeepSeek API to generate a blog article."""
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    prompt = f"""你是一位专业的技术博客写手，为NexTool（一个在线AI效率工具平台）撰写SEO优化的博客文章。

请根据以下主题写一篇博客文章：
- 标题：{topic['title']}
- 关键词：{topic['keywords']}
- 关联工具：{topic['tool']}（工具链接：{BASE_URL}/{topic['tool']}/）

要求：
1. 文章长度1500-2500字
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
  "content_html": "文章正文的HTML内容（h2, h3, p, ul, ol, blockquote标签）",
  "faq_html": "FAQ部分的HTML内容",
  "conclusion_html": "总结部分的HTML内容"
}}"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一位专业的中文技术博客写手，擅长撰写SEO优化的实用指南类文章。输出必须是纯JSON格式，不要包含markdown代码块标记。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000,
    )

    content = response.choices[0].message.content.strip()
    # Remove markdown code block markers if present
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    try:
        article = json.loads(content)
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse API response as JSON, attempting extraction...")
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            article = json.loads(json_match.group())
        else:
            raise ValueError("Could not extract JSON from API response")

    return article


def create_blog_html(article, topic):
    """Create a complete HTML blog article file."""
    slug = re.sub(r'[^\w\s-]', '', topic["title"].lower())
    slug = re.sub(r'[\s]+', '-', slug)
    filename = f"{slug}.html"
    filepath = os.path.join(BLOG_DIR, filename)
    url = f"{BASE_URL}/blog/{filename}"

    title = article.get("title", topic["title"])
    description = article.get("description", "")
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
<meta name="keywords" content="{topic['keywords']}">
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
  "author": {{"@type": "Organization", "name": "NexTool"}},
  "publisher": {{"@type": "Organization", "name": "NexTool"}},
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
.cta-btn{{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-radius:50px;text-decoration:none;font-weight:600;font-size:1rem;transition:transform .3s,box-shadow .3s;margin:20px 0}}
.cta-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 25px rgba(168,85,247,0.4)}}
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
    <div class="meta">📅 {TODAY} · 📖 阅读约8分钟 · 🏷️ {topic['keywords'].split(',')[0]}</div>
    {content_html}
    <h2>常见问题</h2>
    {faq_html}
    <h2>总结</h2>
    {conclusion_html}
    <div style="text-align:center;margin:32px 0">
      <a href="{BASE_URL}/{topic['tool']}/" class="cta-btn">🚀 立即体验{topic['keywords'].split(',')[0]}工具</a>
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
</body>
</html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Blog article created: {filepath}")
    print(f"   URL: {url}")
    return filename


def main():
    print(f"🤖 Daily SEO Article Generator - {TODAY}")

    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("❌ DEEPSEEK_API_KEY not set, skipping article generation.")
        return

    topic = select_topic()
    print(f"📋 Selected topic: {topic['title']}")

    try:
        article = generate_article(topic)
        filename = create_blog_html(article, topic)
        print(f"🎉 Successfully generated blog article: {filename}")
    except Exception as e:
        print(f"❌ Failed to generate article: {e}")
        raise


if __name__ == "__main__":
    main()
