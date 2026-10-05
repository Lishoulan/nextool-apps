#!/usr/bin/env python3
"""
Rebuild blog/index.html by scanning the actual article files in blog/.

Replaces the hand-maintained index page that was lost when a
`git add -A` commit removed it (June 2026). Reads each article's real
<title> and meta description so the index never drifts into dead links.
"""

import os
import re
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BLOG_DIR = REPO_ROOT / "blog"
SITE = "https://lishoulan.github.io/nextool-apps"

CATEGORY_RULES = [
    (r"翻译|translate|translation", "AI翻译"),
    (r"简历|resume", "求职简历"),
    (r"ppt|演示|幻灯", "PPT生成"),
    (r"合同|contract", "合同生成"),
    (r"论文|paper|学术", "学术写作"),
    (r"代码|编程|code", "开发者"),
    (r"pdf", "PDF工具"),
    (r"摘要|总结", "效率工具"),
    (r"邮件|email|mail", "办公效率"),
    (r"时间戳|unix|timestamp", "开发工具"),
    (r"base64|编码|url|正则|json|markdown|二维码|qr", "开发工具"),
    (r"密码|计算器|字数|图片|色彩|color", "效率工具"),
]


def categorize(name: str, title: str) -> str:
    haystack = f"{name} {title}".lower()
    for pattern, label in CATEGORY_RULES:
        if re.search(pattern, haystack):
            return label
    return "AI工具"


def read_meta(path: Path) -> tuple[str, str, str]:
    """Return (title, description, date) from an article file."""
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem, "", ""

    title = ""
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if m:
        title = m.group(1).strip()
        # strip the trailing "| NexTool博客" suffix
        title = re.split(r"\s*[|｜]\s*", title)[0].strip()
    if not title:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S | re.I)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    if not title:
        title = path.stem

    desc = ""
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.S | re.I)
    if m:
        desc = m.group(1).strip()

    date = ""
    m = re.search(r'<meta\s+(?:property|name)=["\'](?:article:published_time|date)["\']\s+content=["\'](.*?)["\']', html, re.S | re.I)
    if m:
        date = m.group(1).strip()[:10]
    if not date:
        m = re.search(r"(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})", path.stem)
        if m:
            date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    if not date:
        # Articles carry no publish-time metadata, so fall back to the first
        # plausible date mentioned in the body before resorting to mtime.
        m = re.search(r"(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})", html)
        if m:
            date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    if not date:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        date = mtime.strftime("%Y-%m-%d")

    return title, desc, date


def build():
    articles = []
    for f in sorted(BLOG_DIR.glob("*.html")):
        if f.name == "index.html":
            continue
        title, desc, date = read_meta(f)
        articles.append(
            {
                "file": f.name,
                "title": title,
                "desc": desc,
                "date": date,
                "cat": categorize(f.stem, title),
            }
        )

    articles.sort(key=lambda a: a["date"], reverse=True)

    cats: dict[str, int] = {}
    for a in articles:
        cats[a["cat"]] = cats.get(a["cat"], 0) + 1

    cards = "\n".join(
        f'''    <a href="./{a["file"]}" class="card">
      <span class="tag">{a["cat"]}</span>
      <h2>{a["title"]}</h2>
      <p>{a["desc"] or a["title"]}</p>
      <div class="meta">{a["date"]}</div>
    </a>'''
        for a in articles
    )

    chips = "".join(
        f'<span class="chip">{c} <b>{n}</b></span>' for c, n in sorted(cats.items(), key=lambda x: -x[1])
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NexTool 博客 - AI工具使用技巧与行业洞察</title>
<meta name="description" content="NexTool博客，分享AI工具使用技巧、效率提升方法和行业洞察。PDF工具、AI简历优化、PPT生成等实用教程。">
<meta name="keywords" content="NexTool博客,AI工具教程,效率提升,PDF工具,AI简历,PPT生成,在线工具">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{SITE}/blog/">
<meta property="og:title" content="NexTool 博客 - AI工具使用技巧与行业洞察">
<meta property="og:description" content="分享AI工具使用技巧、效率提升方法和行业洞察">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/blog/">
<meta property="og:site_name" content="NexTool">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#0f0c29;--bg2:#302b63;--bg3:#24243e;--accent:#00d2ff;--accent2:#3a7bd5;--text:#e8e6e3;--dim:#9a9aaa;--card:rgba(255,255,255,.06);--bd:rgba(255,255,255,.1);--r:12px}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:linear-gradient(135deg,var(--bg),var(--bg2),var(--bg3));color:var(--text);line-height:1.6;min-height:100vh}}
.nav{{position:sticky;top:0;z-index:100;backdrop-filter:blur(20px);background:rgba(15,12,41,.85);border-bottom:1px solid var(--bd);padding:14px 24px;display:flex;align-items:center;justify-content:space-between}}
.nav-logo{{font-size:1.2rem;font-weight:700;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-decoration:none}}
.nav-links{{display:flex;gap:20px;list-style:none}}
.nav-links a{{color:var(--dim);text-decoration:none;font-size:.9rem;transition:color .3s}}
.nav-links a:hover{{color:#fff}}
.container{{max-width:1100px;margin:0 auto;padding:32px 20px}}
.hero{{text-align:center;padding:40px 0 20px}}
.hero h1{{font-size:2rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px}}
.hero p{{color:var(--dim);font-size:1rem;max-width:600px;margin:0 auto}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:20px}}
.chip{{background:var(--card);border:1px solid var(--bd);border-radius:20px;padding:4px 12px;font-size:.78rem;color:var(--dim)}}
.chip b{{color:var(--accent);margin-left:4px}}
.posts{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-top:28px}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:var(--r);padding:24px;text-decoration:none;color:var(--text);transition:transform .2s,box-shadow .2s,border-color .2s;display:flex;flex-direction:column}}
.card:hover{{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,210,255,.1);border-color:var(--accent)}}
.tag{{display:inline-block;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-size:.75rem;font-weight:600;padding:3px 10px;border-radius:20px;margin-bottom:12px;align-self:flex-start}}
.card h2{{font-size:1.15rem;font-weight:700;margin-bottom:8px;line-height:1.4}}
.card p{{font-size:.9rem;color:var(--dim);line-height:1.6;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.meta{{font-size:.8rem;color:var(--dim);margin-top:12px;opacity:.7}}
footer{{text-align:center;padding:32px;color:var(--dim);font-size:.8rem;border-top:1px solid var(--bd);margin-top:40px}}
footer a{{color:var(--accent);text-decoration:none}}
@media(max-width:640px){{.posts{{grid-template-columns:1fr}}.hero h1{{font-size:1.5rem}}}}
</style>
</head>
<body>
<nav class="nav">
  <a href="{SITE}/" class="nav-logo">⚡ NexTool</a>
  <ul class="nav-links">
    <li><a href="{SITE}/">首页</a></li>
    <li><a href="./index.html">博客</a></li>
  </ul>
</nav>
<div class="container">
  <div class="hero">
    <h1>NexTool 博客</h1>
    <p>AI工具使用技巧、效率提升方法与行业洞察 · 共 {len(articles)} 篇</p>
    <div class="chips">{chips}</div>
  </div>
  <div class="posts">
{cards}
  </div>
</div>
<footer>
  <p>© 2025 NexTool. All rights reserved. | <a href="{SITE}/">返回首页</a></p>
</footer>
</body>
</html>
'''


if __name__ == "__main__":
    html = build()
    out = BLOG_DIR / "index.html"
    out.write_text(html, encoding="utf-8")
    n = html.count('class="card"')
    print(f"✅ blog/index.html rebuilt: {n} articles, {len(html)} bytes")
