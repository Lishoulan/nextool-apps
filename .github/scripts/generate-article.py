#!/usr/bin/env python3
"""
Daily blog article generator for NextTool.
Uses DeepSeek API to generate SEO-optimized blog articles.
Falls back to template-based generation if API is unavailable.
Creates HTML files in the blog/ directory.
"""

import json
import os
import re
import random
from datetime import datetime, timezone
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

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


def generate_article_api(topic):
    """Use SiliconFlow (DeepSeek V3) API to generate a blog article."""
    if OpenAI is None:
        raise ImportError("openai package not installed")

    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        raise ValueError("No API key found (DEEPSEEK_API_KEY or SILICONFLOW_API_KEY)")

    client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
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

    model_name = os.environ.get("LLM_MODEL", "deepseek-ai/DeepSeek-V3")
    response = client.chat.completions.create(
        model=model_name,
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


def generate_article_template(topic):
    """Generate article using pre-built templates (fallback when API unavailable)."""
    title = topic['title']
    keywords = topic['keywords']
    kw_list = [k.strip() for k in keywords.split(',')]
    tool = topic['tool']
    tool_url = f"{BASE_URL}/{tool}/"
    main_kw = kw_list[0]

    # Tool display names
    tool_names = {
        'ai-summarizer': 'AI智能摘要', 'json-formatter': 'JSON格式化工具',
        'ai-contract-generator': 'AI合同生成器', 'password-generator': '密码生成器',
        'markdown-editor': 'Markdown编辑器', 'color-picker': '颜色选择器',
        'regex-tester': '正则表达式测试工具', 'ai-resume-optimizer': 'AI简历优化工具',
        'image-compressor': '图片压缩工具', 'base64-tool': 'Base64编码解码工具',
        'url-tool': 'URL编码解码工具', 'timestamp-tool': '时间戳转换工具',
        'word-counter': '字数统计工具', 'ai-translator': 'AI翻译工具',
        'ai-ppt-generator': 'AI PPT生成器', 'ai-paper-rewriter': 'AI论文改写工具',
        'calculator': '科学计算器', 'qr-generator': 'QR码生成器',
        'ai-email-writer': 'AI邮件写作助手', 'ai-code-explainer': 'AI代码解释器',
        'pdf-toolkit': 'PDF工具箱',
    }
    tool_name = tool_names.get(tool, main_kw)

    desc = f"详细介绍{main_kw}的使用方法、技巧和最佳实践。NexTool提供免费在线{main_kw}，无需注册即开即用。"

    content_html = f"""<h2>什么是{main_kw}？</h2>
<p>在数字化时代，{main_kw}已经成为许多人日常工作和学习中不可或缺的工具。无论你是学生、职场人士还是自由职业者，掌握{main_kw}的使用方法都能大幅提升你的工作效率。</p>
<p><a href="{BASE_URL}/">NexTool</a>平台提供的免费在线{main_kw}，无需下载安装，打开浏览器即可使用，非常方便。</p>

<h2>{main_kw}的核心功能与优势</h2>
<p>市面上有很多{main_kw}，但选择一个好用的工具至关重要。以下是优质{main_kw}应具备的核心功能：</p>
<ul>
<li><strong>操作简单</strong> — 直观的界面设计，新手也能快速上手</li>
<li><strong>处理速度快</strong> — 基于云端计算，大文件也能秒级处理</li>
<li><strong>结果精准</strong> — 采用先进的AI算法，确保输出质量</li>
<li><strong>隐私安全</strong> — 数据不上传服务器，保护用户隐私</li>
<li><strong>完全免费</strong> — 基础功能无需付费，零门槛使用</li>
</ul>

<h2>如何使用{tool_name}？详细步骤指南</h2>
<p>使用NexTool的<a href="{tool_url}">{tool_name}</a>非常简单，只需以下几个步骤：</p>
<ol>
<li><strong>打开工具</strong>：访问 <a href="{tool_url}">{tool_name}</a> 页面</li>
<li><strong>输入内容</strong>：在输入框中粘贴或上传你需要处理的内容</li>
<li><strong>调整设置</strong>：根据需要选择相关参数和选项</li>
<li><strong>开始处理</strong>：点击处理按钮，等待几秒即可</li>
<li><strong>获取结果</strong>：查看并下载处理后的结果</li>
</ol>
<blockquote>💡 <strong>小贴士</strong>：对于复杂任务，建议先使用小样本测试效果，满意后再批量处理。</blockquote>

<h2>{main_kw}的实际应用场景</h2>
<p>{main_kw}在实际工作中有着广泛的应用场景：</p>
<ul>
<li><strong>学生群体</strong>：论文写作、课程作业、资料整理</li>
<li><strong>职场人士</strong>：报告撰写、数据分析、文档处理</li>
<li><strong>自由职业者</strong>：客户交付、内容创作、项目交付</li>
<li><strong>开发者</strong>：代码调试、技术文档、API测试</li>
</ul>
<p>无论你属于哪个群体，善用{main_kw}都能帮你节省大量重复劳动的时间。</p>

<h2>选择{main_kw}时需要注意什么？</h2>
<p>在众多{main_kw}中做选择时，以下几点值得重点关注：</p>
<ul>
<li>是否支持中文界面和中文内容处理</li>
<li>免费额度是否足够日常使用</li>
<li>是否有文件大小或长度限制</li>
<li>处理结果的准确性和可用性</li>
<li>是否提供API接口供开发者集成</li>
</ul>
<p>综合以上因素，NexTool的<a href="{tool_url}">{tool_name}</a>在这些方面表现均衡，是一个值得尝试的选择。</p>"""

    faq_html = f"""<ul>
<li><strong>Q: {main_kw}是否免费？</strong><br>A: NexTool提供的{main_kw}基础功能完全免费，Pro用户可享受无限使用次数。</li>
<li><strong>Q: 数据安全吗？</strong><br>A: 所有处理均在浏览器端完成，数据不会上传到服务器，确保您的隐私安全。</li>
<li><strong>Q: 支持哪些设备和浏览器？</strong><br>A: 支持所有现代浏览器（Chrome、Firefox、Safari、Edge），电脑和手机均可使用。</li>
<li><strong>Q: 处理结果不满意怎么办？</strong><br>A: 可以尝试调整输入内容或参数设置，Pro用户还可享受优先客服支持。</li>
</ul>"""

    conclusion_html = f"""<p>{main_kw}是提升工作和学习效率的实用工具。通过本文的介绍，相信你已经对如何选择和使用{main_kw}有了更清晰的认识。</p>
<p>NexTool平台提供包括{tool_name}在内的<a href="{BASE_URL}/">25+款免费AI效率工具</a>，无需注册即可使用。如果你需要更高级的功能，也可以考虑升级到Pro版本，首月仅需¥9.9。</p>
<p>希望这篇文章对你有帮助，快去试试吧！</p>"""

    return {
        'title': title,
        'description': desc,
        'content_html': content_html,
        'faq_html': faq_html,
        'conclusion_html': conclusion_html,
    }


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

    topic = select_topic()
    print(f"📋 Selected topic: {topic['title']}")

    article = None

    # Try API-based generation first
    has_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("SILICONFLOW_API_KEY")
    if has_key:
        try:
            print("📡 Attempting API-based generation (SiliconFlow)...")
            article = generate_article_api(topic)
            print("✅ API generation successful")
        except Exception as e:
            err_msg = str(e)
            if "402" in err_msg or "Insufficient Balance" in err_msg:
                print("⚠️ API balance insufficient, switching to template fallback")
            elif "429" in err_msg or "rate" in err_msg.lower():
                print("⚠️ API rate limited, switching to template fallback")
            else:
                print(f"⚠️ API generation failed: {e}")
                print("📝 Switching to template-based generation...")
    else:
        print("ℹ️ DEEPSEEK_API_KEY not set, using template-based generation")

    # Fallback to template-based generation
    if article is None:
        article = generate_article_template(topic)
        print("✅ Template generation successful")

    try:
        filename = create_blog_html(article, topic)
        print(f"🎉 Blog article created: {filename}")
    except Exception as e:
        print(f"❌ Failed to create blog file: {e}")
        raise


if __name__ == "__main__":
    main()
