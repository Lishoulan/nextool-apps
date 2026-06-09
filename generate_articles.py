import requests
import time
import os

API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = "sk-9b6810e1429747e3ac6f4975926aaec6"
MODEL = "deepseek-chat"
OUTPUT_DIR = r"d:\100\nextool-apps\blog\articles"
NEXTOOL_URL = "https://lishoulan.github.io/nextool-apps/"

articles = [
    {
        "filename": "ai-email-writing-guide.md",
        "title": "AI邮件写作器：10种场景一键生成专业邮件",
        "description": "详细介绍AI邮件写作器在10种常见场景下的应用，包括商务邀请、客户跟进、求职应聘等，教你如何用AI一键生成专业得体的邮件内容。",
        "keywords": ["AI邮件写作", "邮件生成器", "AI写邮件", "专业邮件模板", "商务邮件"],
        "slug": "ai-email-writing-guide",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"AI邮件写作器：10种场景一键生成专业邮件"。

要求：
1. 文章开头加上YAML front matter：
---
title: "AI邮件写作器：10种场景一键生成专业邮件"
description: "详细介绍AI邮件写作器在10种常见场景下的应用，包括商务邀请、客户跟进、求职应聘等，教你如何用AI一键生成专业得体的邮件内容。"
keywords: ["AI邮件写作", "邮件生成器", "AI写邮件", "专业邮件模板", "商务邮件"]
date: "2026-06-08"
slug: "ai-email-writing-guide"
---

2. 文章结构：
- 引人入胜的开头，描述写邮件的痛点
- 为什么需要AI邮件写作器
- 10种场景详细介绍（商务邀请、客户跟进、求职应聘、项目汇报、请假申请、投诉建议、感谢信、会议纪要、合作洽谈、节日祝福）
- AI邮件写作的优势
- 总结与推荐

3. SEO优化：自然融入关键词"AI邮件写作"、"邮件生成器"、"AI写邮件"、"专业邮件"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即体验NextTool AI邮件写作器 → 一键生成专业邮件，告别写作焦虑](https://lishoulan.github.io/nextool-apps/ai-email-writer/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "free-json-formatter-online.md",
        "title": "免费在线JSON格式化工具推荐",
        "description": "全面推荐免费在线JSON格式化工具，对比功能特点，教你如何选择最适合的JSON格式化、校验和压缩工具。",
        "keywords": ["JSON格式化", "在线JSON工具", "JSON校验", "JSON压缩", "JSON编辑器"],
        "slug": "free-json-formatter-online",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"免费在线JSON格式化工具推荐"。

要求：
1. 文章开头加上YAML front matter：
---
title: "免费在线JSON格式化工具推荐"
description: "全面推荐免费在线JSON格式化工具，对比功能特点，教你如何选择最适合的JSON格式化、校验和压缩工具。"
keywords: ["JSON格式化", "在线JSON工具", "JSON校验", "JSON压缩", "JSON编辑器"]
date: "2026-06-08"
slug: "free-json-formatter-online"
---

2. 文章结构：
- 开头描述JSON格式化的痛点
- JSON格式化工具的核心功能需求
- 推荐多款在线JSON格式化工具（重点推荐NextTool）
- JSON格式化常见问题与技巧
- 总结与推荐

3. SEO优化：自然融入关键词"JSON格式化"、"在线JSON工具"、"JSON校验"、"JSON压缩"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool免费JSON格式化工具 → 一键格式化、校验、压缩JSON](https://lishoulan.github.io/nextool-apps/json-formatter/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "regex-tester-online.md",
        "title": "在线正则表达式测试工具使用指南",
        "description": "详细介绍在线正则表达式测试工具的使用方法，从基础语法到高级技巧，帮你快速掌握正则表达式并提高开发效率。",
        "keywords": ["正则表达式测试", "在线正则工具", "regex测试", "正则表达式教程", "正则匹配"],
        "slug": "regex-tester-online",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"在线正则表达式测试工具使用指南"。

要求：
1. 文章开头加上YAML front matter：
---
title: "在线正则表达式测试工具使用指南"
description: "详细介绍在线正则表达式测试工具的使用方法，从基础语法到高级技巧，帮你快速掌握正则表达式并提高开发效率。"
keywords: ["正则表达式测试", "在线正则工具", "regex测试", "正则表达式教程", "正则匹配"]
date: "2026-06-08"
slug: "regex-tester-online"
---

2. 文章结构：
- 开头引入正则表达式的重要性
- 在线正则测试工具的优势
- 如何使用在线正则测试工具（以NextTool为例详细讲解）
- 常用正则表达式速查表
- 正则调试技巧与常见坑
- 总结与推荐

3. SEO优化：自然融入关键词"正则表达式测试"、"在线正则工具"、"regex测试"、"正则匹配"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool在线正则测试工具 → 实时匹配高亮，快速调试正则表达式](https://lishoulan.github.io/nextool-apps/regex-tester/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "ai-code-explainer-review.md",
        "title": "AI代码解释器：30+编程语言逐行解释",
        "description": "深度评测AI代码解释器，支持30+编程语言的逐行解释功能，帮助初学者和开发者快速理解复杂代码逻辑。",
        "keywords": ["AI代码解释器", "代码解释工具", "AI理解代码", "编程语言解释", "代码逐行解释"],
        "slug": "ai-code-explainer-review",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"AI代码解释器：30+编程语言逐行解释"。

要求：
1. 文章开头加上YAML front matter：
---
title: "AI代码解释器：30+编程语言逐行解释"
description: "深度评测AI代码解释器，支持30+编程语言的逐行解释功能，帮助初学者和开发者快速理解复杂代码逻辑。"
keywords: ["AI代码解释器", "代码解释工具", "AI理解代码", "编程语言解释", "代码逐行解释"]
date: "2026-06-08"
slug: "ai-code-explainer-review"
---

2. 文章结构：
- 开头描述阅读他人代码的痛点
- AI代码解释器是什么，如何工作
- 支持的30+编程语言分类介绍
- 实际使用案例（Python、JavaScript、Go等）
- AI代码解释器vs传统方法对比
- 适用人群与使用场景
- 总结与推荐

3. SEO优化：自然融入关键词"AI代码解释器"、"代码解释工具"、"AI理解代码"、"代码逐行解释"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即体验NextTool AI代码解释器 → 粘贴代码，逐行解释，30+语言全覆盖](https://lishoulan.github.io/nextool-apps/ai-code-explainer/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "password-generator-security.md",
        "title": "密码生成器：如何创建安全的随机密码",
        "description": "全面讲解密码生成器的安全原理，教你如何创建高强度随机密码，对比手动设置密码与密码生成器的安全性差异。",
        "keywords": ["密码生成器", "随机密码", "强密码", "密码安全", "密码强度"],
        "slug": "password-generator-security",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"密码生成器：如何创建安全的随机密码"。

要求：
1. 文章开头加上YAML front matter：
---
title: "密码生成器：如何创建安全的随机密码"
description: "全面讲解密码生成器的安全原理，教你如何创建高强度随机密码，对比手动设置密码与密码生成器的安全性差异。"
keywords: ["密码生成器", "随机密码", "强密码", "密码安全", "密码强度"]
date: "2026-06-08"
slug: "password-generator-security"
---

2. 文章结构：
- 开头用数据说明密码安全的重要性
- 为什么手动设置密码不安全
- 密码生成器的工作原理
- 如何创建安全的随机密码（长度、复杂度、唯一性）
- 密码强度评估标准
- 密码管理最佳实践
- 总结与推荐

3. SEO优化：自然融入关键词"密码生成器"、"随机密码"、"强密码"、"密码安全"、"密码强度"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool免费密码生成器 → 一键创建安全的强密码](https://lishoulan.github.io/nextool-apps/password-generator/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "qrcode-generator-tutorial.md",
        "title": "二维码生成器使用教程：自定义颜色和Logo",
        "description": "详细的二维码生成器使用教程，教你如何自定义二维码颜色、添加Logo、调整样式，生成个性化的二维码。",
        "keywords": ["二维码生成器", "自定义二维码", "二维码加Logo", "二维码颜色", "在线生成二维码"],
        "slug": "qrcode-generator-tutorial",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"二维码生成器使用教程：自定义颜色和Logo"。

要求：
1. 文章开头加上YAML front matter：
---
title: "二维码生成器使用教程：自定义颜色和Logo"
description: "详细的二维码生成器使用教程，教你如何自定义二维码颜色、添加Logo、调整样式，生成个性化的二维码。"
keywords: ["二维码生成器", "自定义二维码", "二维码加Logo", "二维码颜色", "在线生成二维码"]
date: "2026-06-08"
slug: "qrcode-generator-tutorial"
---

2. 文章结构：
- 开头介绍二维码的广泛应用
- 二维码生成器的基本功能
- 详细教程：如何自定义颜色（前景色、背景色选择技巧）
- 详细教程：如何添加Logo（Logo大小、位置、容错率设置）
- 二维码设计最佳实践
- 常见问题解答
- 总结与推荐

3. SEO优化：自然融入关键词"二维码生成器"、"自定义二维码"、"二维码加Logo"、"二维码颜色"、"在线生成二维码"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool免费二维码生成器 → 自定义颜色、添加Logo，生成个性化二维码](https://lishoulan.github.io/nextool-apps/qr-generator/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "markdown-editor-online.md",
        "title": "在线Markdown编辑器推荐：实时预览导出HTML",
        "description": "推荐最佳在线Markdown编辑器，支持实时预览、导出HTML、多种主题切换，帮你高效撰写和排版Markdown文档。",
        "keywords": ["Markdown编辑器", "在线Markdown", "Markdown预览", "Markdown转HTML", "Markdown写作"],
        "slug": "markdown-editor-online",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"在线Markdown编辑器推荐：实时预览导出HTML"。

要求：
1. 文章开头加上YAML front matter：
---
title: "在线Markdown编辑器推荐：实时预览导出HTML"
description: "推荐最佳在线Markdown编辑器，支持实时预览、导出HTML、多种主题切换，帮你高效撰写和排版Markdown文档。"
keywords: ["Markdown编辑器", "在线Markdown", "Markdown预览", "Markdown转HTML", "Markdown写作"]
date: "2026-06-08"
slug: "markdown-editor-online"
---

2. 文章结构：
- 开头描述Markdown的流行和编辑需求
- 在线Markdown编辑器的核心功能需求
- 推荐几款在线Markdown编辑器（重点推荐NextTool）
- 实时预览功能详解
- 导出HTML和其他格式的方法
- Markdown写作技巧
- 总结与推荐

3. SEO优化：自然融入关键词"Markdown编辑器"、"在线Markdown"、"Markdown预览"、"Markdown转HTML"、"Markdown写作"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool在线Markdown编辑器 → 实时预览，一键导出HTML](https://lishoulan.github.io/nextool-apps/markdown-editor/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "image-compressor-online.md",
        "title": "在线图片压缩工具：批量压缩不上传服务器",
        "description": "介绍安全的在线图片压缩工具，支持批量压缩且图片不上传服务器，保护隐私的同时高效压缩JPG、PNG、WebP等格式。",
        "keywords": ["图片压缩", "在线压缩", "批量压缩图片", "图片不上传服务器", "图片压缩工具"],
        "slug": "image-compressor-online",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"在线图片压缩工具：批量压缩不上传服务器"。

要求：
1. 文章开头加上YAML front matter：
---
title: "在线图片压缩工具：批量压缩不上传服务器"
description: "介绍安全的在线图片压缩工具，支持批量压缩且图片不上传服务器，保护隐私的同时高效压缩JPG、PNG、WebP等格式。"
keywords: ["图片压缩", "在线压缩", "批量压缩图片", "图片不上传服务器", "图片压缩工具"]
date: "2026-06-08"
slug: "image-compressor-online"
---

2. 文章结构：
- 开头描述图片压缩的需求和隐私担忧
- 为什么选择不上传服务器的压缩工具
- 本地压缩vs服务器端压缩的技术原理
- 推荐几款安全的在线图片压缩工具（重点推荐NextTool）
- 批量压缩的使用技巧
- 不同图片格式的压缩策略
- 总结与推荐

3. SEO优化：自然融入关键词"图片压缩"、"在线压缩"、"批量压缩图片"、"图片不上传服务器"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool在线图片压缩工具 → 批量压缩，图片不上传服务器，安全高效](https://lishoulan.github.io/nextool-apps/image-compressor/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "color-picker-css-gradient.md",
        "title": "颜色选择器与CSS渐变生成器",
        "description": "详细介绍在线颜色选择器和CSS渐变生成器的使用方法，教你如何选取完美配色方案并生成线性渐变、径向渐变CSS代码。",
        "keywords": ["颜色选择器", "CSS渐变", "渐变生成器", "在线取色器", "CSS渐变代码"],
        "slug": "color-picker-css-gradient",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"颜色选择器与CSS渐变生成器"。

要求：
1. 文章开头加上YAML front matter：
---
title: "颜色选择器与CSS渐变生成器"
description: "详细介绍在线颜色选择器和CSS渐变生成器的使用方法，教你如何选取完美配色方案并生成线性渐变、径向渐变CSS代码。"
keywords: ["颜色选择器", "CSS渐变", "渐变生成器", "在线取色器", "CSS渐变代码"]
date: "2026-06-08"
slug: "color-picker-css-gradient"
---

2. 文章结构：
- 开头描述前端开发中配色和渐变的需求
- 颜色选择器的核心功能（HEX、RGB、HSL转换）
- CSS渐变类型详解（线性渐变、径向渐变、锥形渐变）
- 如何使用渐变生成器创建美观的渐变效果
- 配色方案推荐与技巧
- CSS渐变代码最佳实践
- 总结与推荐

3. SEO优化：自然融入关键词"颜色选择器"、"CSS渐变"、"渐变生成器"、"在线取色器"、"CSS渐变代码"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool颜色选择器 → 选取配色、生成CSS渐变代码，前端开发必备](https://lishoulan.github.io/nextool-apps/color-picker/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    },
    {
        "filename": "timestamp-converter-tool.md",
        "title": "时间戳转换工具：多时区支持",
        "description": "详细介绍时间戳转换工具的使用方法，支持Unix时间戳与日期时间互转、多时区切换，满足开发者和运维人员的日常需求。",
        "keywords": ["时间戳转换", "Unix时间戳", "时间戳工具", "时区转换", "在线时间戳"],
        "slug": "timestamp-converter-tool",
        "prompt": """请写一篇1500-2500字的中文SEO博客文章，标题为"时间戳转换工具：多时区支持"。

要求：
1. 文章开头加上YAML front matter：
---
title: "时间戳转换工具：多时区支持"
description: "详细介绍时间戳转换工具的使用方法，支持Unix时间戳与日期时间互转、多时区切换，满足开发者和运维人员的日常需求。"
keywords: ["时间戳转换", "Unix时间戳", "时间戳工具", "时区转换", "在线时间戳"]
date: "2026-06-08"
slug: "timestamp-converter-tool"
---

2. 文章结构：
- 开头描述时间戳在开发中的重要性
- 什么是Unix时间戳
- 时间戳转换工具的核心功能
- 多时区支持详解（UTC、GMT、各主要时区）
- 时间戳在各类编程语言中的使用
- 常见时间戳问题与解决方案
- 总结与推荐

3. SEO优化：自然融入关键词"时间戳转换"、"Unix时间戳"、"时间戳工具"、"时区转换"、"在线时间戳"等
4. 至少2处自然提及NextTool并附上链接 https://lishoulan.github.io/nextool-apps/
5. 文章末尾添加推广footer：
---
👉 **[立即使用NextTool时间戳转换工具 → Unix时间戳互转，多时区支持，开发者必备](https://lishoulan.github.io/nextool-apps/timestamp-tool/)**
6. 直接输出Markdown格式内容，不要加代码块包裹"""
    }
]


def generate_article(article_info):
    """调用DeepSeek API生成文章"""
    print(f"正在生成: {article_info['filename']}")

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的中文技术博客写手，擅长撰写SEO优化的技术文章。直接输出Markdown格式内容，不要用代码块包裹。"
                    },
                    {
                        "role": "user",
                        "content": article_info["prompt"]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            },
            timeout=120
        )

        if response.status_code != 200:
            print(f"  API错误: HTTP {response.status_code}")
            print(f"  响应: {response.text[:500]}")
            return None

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # 清理可能的markdown代码块包裹
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            content = "\n".join(lines[1:-1])

        return content

    except Exception as e:
        print(f"  生成失败: {e}")
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    success_count = 0
    fail_count = 0

    for i, article in enumerate(articles):
        print(f"\n[{i+1}/{len(articles)}] 生成文章: {article['title']}")

        content = generate_article(article)

        if content:
            filepath = os.path.join(OUTPUT_DIR, article["filename"])
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✓ 已保存: {filepath}")
            print(f"  字数: {len(content)}")
            success_count += 1
        else:
            print(f"  ✗ 生成失败: {article['filename']}")
            fail_count += 1

        # 每篇文章之间间隔5秒，避免API限流
        if i < len(articles) - 1:
            print("  等待5秒...")
            time.sleep(5)

    print(f"\n{'='*50}")
    print(f"生成完成！成功: {success_count}, 失败: {fail_count}")


if __name__ == "__main__":
    main()
