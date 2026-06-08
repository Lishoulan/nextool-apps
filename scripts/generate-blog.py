#!/usr/bin/env python3
"""
Auto blog article generator for NextTool.
Uses DeepSeek API (OpenAI-compatible) to generate SEO-optimized Markdown blog articles.
Creates .md files in the blog/articles/ directory.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

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
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

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

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一位专业的中文技术博客写手，擅长撰写SEO优化的实用指南类文章。直接输出Markdown格式内容。",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4000,
    )

    content = response.choices[0].message.content.strip()
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
