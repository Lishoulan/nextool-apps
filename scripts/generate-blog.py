#!/usr/bin/env python3
"""
Auto blog article generator for NextTool.
Uses DeepSeek API (OpenAI-compatible) to generate SEO-optimized Markdown blog articles.
Creates .md files in the blog/articles/ directory.
"""

import json
import os
import re
import requests
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLOG_DIR = os.path.join(REPO_ROOT, "blog", "articles")
BASE_URL = "https://lishoulan.github.io/nextool-apps"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Predefined topic list for rotation
TOPICS = [
    {
        "title": "5个免费AI工具提升工作效率",
        "keywords": "AI工具,免费工具,工作效率,效率提升,在线工具",
        "slug": "5-free-ai-tools-boost-productivity",
    },
    {
        "title": "PDF合并拆分压缩一站式解决方案",
        "keywords": "PDF合并,PDF拆分,PDF压缩,免费PDF工具,在线PDF",
        "slug": "pdf-merge-split-compress-solution",
    },
    {
        "title": "AI简历优化器如何提高面试通过率",
        "keywords": "AI简历优化,简历写作,面试技巧,求职工具,简历模板",
        "slug": "ai-resume-optimizer-interview-tips",
    },
    {
        "title": "3分钟生成PPT的AI工具推荐",
        "keywords": "AI生成PPT,PPT制作,演示文稿,办公效率,PPT工具",
        "slug": "ai-ppt-generator-3-minutes",
    },
    {
        "title": "论文降重工具对比评测",
        "keywords": "论文降重,查重工具,学术写作,降重方法,论文修改",
        "slug": "paper-plagiarism-reduction-tools-review",
    },
    {
        "title": "免费合同生成器使用指南",
        "keywords": "合同生成器,免费合同,法律文书,合同模板,在线工具",
        "slug": "free-contract-generator-guide",
    },
    {
        "title": "AI翻译工具哪个好",
        "keywords": "AI翻译,翻译工具,多语言翻译,在线翻译,翻译对比",
        "slug": "ai-translation-tools-comparison",
    },
    {
        "title": "程序员必备的10个在线工具",
        "keywords": "程序员工具,在线工具,开发工具,效率工具,编程工具",
        "slug": "10-must-have-online-tools-for-developers",
    },
    {
        "title": "学生党必备的免费工具箱",
        "keywords": "学生工具,免费工具,学习工具,效率工具,学生必备",
        "slug": "free-toolbox-for-students",
    },
    {
        "title": "远程办公效率工具推荐",
        "keywords": "远程办公,效率工具,在线协作,办公软件,远程工作",
        "slug": "remote-work-efficiency-tools",
    },
]


def get_topic_index():
    """Determine which topic to use based on week number for rotation."""
    week_number = datetime.now(timezone.utc).isocalendar()[1]
    return week_number % len(TOPICS)


def get_existing_slugs():
    """Get set of existing article slugs to avoid duplicates."""
    existing = set()
    if os.path.isdir(BLOG_DIR):
        for f in os.listdir(BLOG_DIR):
            if f.endswith(".md"):
                existing.add(f.replace(".md", ""))
    return existing


def select_topic():
    """Select a topic by rotation, skipping already-covered topics."""
    existing = get_existing_slugs()
    start_index = get_topic_index()

    for i in range(len(TOPICS)):
        index = (start_index + i) % len(TOPICS)
        topic = TOPICS[index]
        if topic["slug"] not in existing:
            return topic

    # If all topics covered, use rotation index with date suffix
    topic = TOPICS[start_index].copy()
    topic["slug"] = f"{topic['slug']}-{TODAY}"
    return topic


def generate_article(topic):
    """Use DeepSeek API to generate a Markdown blog article."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    prompt = f"""你是一位专业的中文技术博客写手，为NexTool（一个在线AI效率工具平台）撰写SEO优化的博客文章。

请根据以下主题写一篇博客文章：
- 标题：{topic['title']}
- 关键词：{topic['keywords']}

要求：
1. 文章长度1500-2500字
2. 使用Markdown格式输出
3. 文章结构：标题 → 引言 → 3-4个正文章节（每个章节有##标题）→ 常见问题（FAQ）→ 总结
4. 自然地融入关键词，不堆砌
5. 在文章中至少2处自然地提及NexTool平台并附上链接 {BASE_URL}/
6. 语气专业但亲切，像朋友间分享经验
7. 包含具体的操作步骤和实用建议
8. FAQ部分包含3-5个常见问题，用###标题
9. 文章末尾包含一段推广信息，引导读者访问NexTool平台

请直接输出Markdown格式的文章内容，不要包含JSON或其他格式包装。"""

    # Try DeepSeek first, fall back to template generation
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    if api_key:
        try:
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位专业的中文技术博客写手，擅长撰写SEO优化的实用指南类文章。直接输出Markdown格式内容。",
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
            return content
        except Exception as e:
            print(f"⚠️ DeepSeek API failed: {e}, using template generation...")
    
    # Template-based generation as fallback
    return generate_article_template(topic)


# Template articles for each topic (used when API is unavailable)
TEMPLATE_ARTICLES = {
    "5-free-ai-tools-boost-productivity": """# 5个免费AI工具提升工作效率

在当今快节奏的工作环境中，AI工具已经成为提升效率的必备利器。本文将为你推荐5个真正免费、无需注册的AI在线工具，让你的工作效率翻倍。

## 1. AI PPT生成器 - 3分钟出完整PPT

做PPT是很多人工作中的噩梦，排版、设计、内容组织，每一项都耗时耗力。而AI PPT生成器可以帮你解决这个问题。

使用方法很简单：输入你的PPT主题，选择风格模板，等待3分钟左右，一套完整的PPT就生成了。生成的PPT包含完整的框架和内容，不是只有标题的空壳。

访问 [NexTool AI PPT生成器]({BASE_URL}/ai-ppt-generator/) 即可免费使用。

## 2. AI简历优化器 - 面试通过率翻倍

求职时最头疼的就是改简历。每个岗位都需要针对性修改，而AI简历优化器可以帮你自动匹配关键词、润色经历描述。

使用步骤：
1. 粘贴你的简历内容
2. 粘贴目标岗位的职位描述（JD）
3. AI自动分析并优化你的简历

访问 [NexTool AI简历优化器]({BASE_URL}/ai-resume-optimizer/) 免费体验。

## 3. AI论文降重 - 保留原意降低查重率

写论文最怕的就是查重率过高。AI论文降重工具可以帮你改写论文段落，降低查重率的同时保留原意。比手动改写效率高很多，而且改写后的表达更流畅。

## 4. AI合同生成器 - 12种合同一键生成

创业者和HR的福音！支持劳动合同、租赁合同、保密协议等12种合同类型，生成后可以一键导出Word文档。

## 5. PDF工具箱 - 6大功能一站搞定

PDF合并、拆分、压缩、转图片、加水印、图片转PDF，6大功能一站搞定。最重要的是所有操作都在浏览器本地完成，文件不会上传到服务器。

访问 [NexTool PDF工具箱]({BASE_URL}/pdf-toolkit/) 免费使用。

## 常见问题

### 这些工具真的免费吗？
是的，NexTool的所有工具都完全免费，没有"试用3次"的限制，也不需要注册。

### 我的文件安全吗？
PDF处理、图片压缩等涉及文件的操作全部在浏览器本地完成，文件不会上传到任何服务器，隐私安全有保障。

### 需要注册账号吗？
不需要！打开网页直接使用，不收集任何个人信息。

## 总结

以上5个AI工具都可以在 [NexTool]({BASE_URL}/) 免费使用，无需注册，打开即用。如果你也有提升效率的需求，不妨试试看！""",

    "pdf-merge-split-compress-solution": """# PDF合并拆分压缩一站式解决方案

处理PDF文件是日常办公最常见的操作之一，但每次都要找各种工具，还动不动就要付费。本文介绍一个一站式的免费PDF解决方案。

## 为什么需要PDF工具？

日常工作中，我们经常需要：
- 把多个PDF合并成一个文件
- 从大PDF中提取需要的页面
- 压缩PDF文件以便邮件发送
- 把PDF页面转为图片分享
- 给PDF添加水印保护版权
- 把多张图片合成PDF

## NexTool PDF工具箱

[NexTool PDF工具箱]({BASE_URL}/pdf-toolkit/) 提供了6大功能：

### PDF合并
选择多个PDF文件，一键合并成一个。适合把分散的扫描件、多份报告合并整理。

### PDF拆分
把大PDF按页码拆分成小文件，提取需要的页面。

### PDF压缩
减小PDF文件体积，解决邮件附件超限的问题。

### PDF转图片
把PDF页面转为JPG/PNG，方便分享单页内容。

### PDF加水印
批量添加文字或图片水印，保护文档版权。

### 图片转PDF
多张图片合成PDF，做电子相册或整理扫描件。

## 隐私安全保障

最关键的是：所有操作都在浏览器本地完成！文件不会上传到服务器。处理工作合同、工资单等敏感文件时完全不用担心隐私泄露。

## 常见问题

### 文件大小有限制吗？
由于是本地处理，文件大小取决于你的浏览器和电脑性能，一般100MB以内的文件都能流畅处理。

### 支持哪些格式？
支持标准PDF格式输入，输出为PDF或JPG/PNG图片格式。

## 总结

如果你需要日常的PDF合并、拆分、压缩，[NexTool PDF工具箱]({BASE_URL}/pdf-toolkit/) 是最省心的选择——免费、无限制、本地处理。""",

    "ai-resume-optimizer-interview-tips": """# AI简历优化器如何提高面试通过率

求职时，简历是第一道门槛。一份好的简历可以帮你通过ATS（简历筛选系统），获得更多面试机会。本文介绍如何使用AI简历优化器提升面试通过率。

## 简历筛选的真相

大多数公司使用ATS系统筛选简历，系统会根据关键词匹配度来决定你的简历是否被HR看到。这意味着即使你的经历很匹配，如果简历里缺少关键词，也可能被系统过滤掉。

## AI简历优化器的工作原理

[NexTool AI简历优化器]({BASE_URL}/ai-resume-optimizer/) 的工作流程：

1. 你提供原始简历内容
2. 你提供目标岗位的职位描述（JD）
3. AI分析JD中的关键词和技能要求
4. AI帮你调整简历措辞，突出匹配的经历
5. 提取关键词确保简历能通过ATS

## 使用效果

实际使用中，优化前投简历回复率约20%，优化后能到40-50%。当然简历只是第一步，面试表现才是关键，但至少能帮你过简历筛选这一关。

## 5个简历优化技巧

1. **每份简历都要针对性调整** - 不同岗位的JD不同，关键词不同
2. **先提取JD关键词** - 确保简历里包含岗位要求的技能和工具
3. **用STAR法则描述经历** - Situation、Task、Action、Result
4. **量化成果** - "提升了效率"不如"效率提升30%"
5. **保持真实性** - AI可以润色措辞，但不要编造不存在的经历

## 常见问题

### AI优化后的简历会被识别吗？
优化后的简历读起来应该像人写的，不会触发AI检测。但建议优化后自己审阅调整。

### 需要付费吗？
[NexTool AI简历优化器]({BASE_URL}/ai-resume-optimizer/) 完全免费，无需注册，打开即用。

## 总结

AI简历优化器是一个很好的辅助工具，特别是免费的，可以反复优化不同版本的简历。访问 [NexTool]({BASE_URL}/) 开始优化你的简历吧！""",

    "ai-ppt-generator-3-minutes": """# 3分钟生成PPT的AI工具推荐

每次做PPT都要熬夜排版？AI PPT生成器可以帮你3分钟出完整PPT，从此告别加班做幻灯片的日子。

## AI PPT生成器是什么？

[NexTool AI PPT生成器]({BASE_URL}/ai-ppt-generator/) 是一个免费的在线工具，输入PPT主题，AI自动生成包含完整框架和内容的演示文稿。

## 使用方法

1. 打开 [AI PPT生成器]({BASE_URL}/ai-ppt-generator/)
2. 输入你的PPT主题（如"2024年度工作总结"）
3. 选择风格模板
4. 等待3分钟左右
5. 获得完整的PPT

## 生成效果

生成的PPT包含：
- 完整的章节结构
- 每页的内容要点
- 排版设计
- 多种风格模板可选

当然，生成后还需要根据实际情况调整细节，但比从零开始做快太多了。

## 配合其他工具使用

- 先用 [AI文本摘要]({BASE_URL}/ai-text-summarizer/) 生成汇报内容的摘要
- 再用AI PPT生成器把摘要变成PPT
- 效率直接翻倍

## 常见问题

### 生成的PPT可以编辑吗？
可以，生成后你可以自由修改内容和样式。

### 需要付费吗？
完全免费，无需注册，打开即用。

## 总结

AI PPT生成器是做汇报、做方案时的效率神器。访问 [NexTool]({BASE_URL}/) 免费体验！""",
}


def generate_article_template(topic):
    """Generate article from template when API is unavailable."""
    slug = topic["slug"]
    
    if slug in TEMPLATE_ARTICLES:
        content = TEMPLATE_ARTICLES[slug]
        # Replace BASE_URL placeholder
        content = content.replace("{BASE_URL}", BASE_URL)
        return content
    
    # Generic template for topics without specific templates
    keywords = topic["keywords"].split(",")
    primary_keyword = keywords[0] if keywords else topic["title"]
    
    content = f"""# {topic['title']}

{primary_keyword}是很多人日常工作和学习中的刚需。本文将为你详细介绍{primary_keyword}的解决方案，以及如何使用免费在线工具提升效率。

## 为什么需要{primary_keyword}？

在日常工作中，我们经常遇到需要{primary_keyword}的场景。传统的做法往往效率低下，而借助AI工具可以大大提升效率。

## 推荐工具：NexTool

[NexTool]({BASE_URL}/) 是一个免费的在线AI工具箱，提供25+个实用工具，包括：

- AI PPT生成器 - 输入主题3分钟出PPT
- AI简历优化器 - 自动匹配关键词润色经历
- AI论文降重 - 改写论文降低查重率
- AI合同生成器 - 12种合同一键导出
- PDF工具箱 - 合并/拆分/压缩一站搞定
- 更多工具...

所有工具完全免费，无需注册，打开即用！

## 使用方法

1. 访问 [NexTool]({BASE_URL}/)
2. 选择你需要的工具
3. 按照提示操作即可

## 特点

- **无需注册**：打开就用，不收集任何信息
- **本地处理**：文件处理在浏览器本地完成，不上传服务器
- **完全免费**：没有付费墙，没有使用次数限制

## 常见问题

### 真的免费吗？
是的，所有工具都完全免费，没有隐藏收费。

### 文件安全吗？
所有文件处理都在浏览器本地完成，不会上传到任何服务器。

## 总结

如果你需要{primary_keyword}，[NexTool]({BASE_URL}/) 是最好的免费选择。无需注册，打开即用！"""
    
    return content


def add_front_matter(content, topic):
    """Add YAML front matter and SEO metadata to the article."""
    front_matter = f"""---
title: "{topic['title']}"
description: "{topic['title']} - NexTool在线工具平台为您提供专业解决方案，包含{topic['keywords'].split(',')[0]}等多种免费工具。"
keywords: "{topic['keywords']}"
author: "NexTool"
date: "{TODAY}"
slug: "{topic['slug']}"
canonical: "{BASE_URL}/blog/articles/{topic['slug']}.html"
---

"""
    return front_matter + content


def add_footer(content):
    """Add NexTool promotional footer to the article."""
    footer = f"""

---

> 🚀 **想要体验更多免费在线AI工具？** 访问 [NexTool - 在线AI效率工具平台]({BASE_URL}/)，我们提供PDF工具、AI简历优化、PPT生成、合同生成、论文降重等数十款免费在线工具，助您效率翻倍！

*本文由NexTool团队发布，转载请注明出处：{BASE_URL}/blog/*
"""
    return content + footer


def save_article(content, topic):
    """Save the generated article as a Markdown file."""
    os.makedirs(BLOG_DIR, exist_ok=True)
    filename = f"{topic['slug']}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Blog article created: {filepath}")
    return filename


def main():
    print(f"🤖 Auto Blog Article Generator - {TODAY}")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not set.")
        raise SystemExit(1)

    topic = select_topic()
    print(f"📋 Selected topic: {topic['title']}")
    print(f"🔗 Slug: {topic['slug']}")

    try:
        raw_content = generate_article(topic)
        content_with_front_matter = add_front_matter(raw_content, topic)
        final_content = add_footer(content_with_front_matter)
        filename = save_article(final_content, topic)
        print(f"🎉 Successfully generated blog article: {filename}")
    except Exception as e:
        print(f"❌ Failed to generate article: {e}")
        raise


if __name__ == "__main__":
    main()
