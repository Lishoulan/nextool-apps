"""
每日SEO内容生成器 - 本地模板方式（不依赖付费API）
从预设模板中随机生成文章，确保每天有新内容
"""
import os
import random
import json
from datetime import datetime

SITE_URL = os.environ.get("SITE_URL", "https://lishoulan.github.io/nextool-apps/")
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "nextool2026indexnow")

# 预设文章模板
ARTICLE_TEMPLATES = [
    {
        "title": "免费AI写作工具推荐：这5个工具让你写作效率翻倍",
        "description": "推荐5个最好用的免费AI写作工具，包括AI文案生成、邮件写作、论文改写等，全部免费使用！",
        "keywords": "免费AI写作工具,AI文案生成,写作效率提升,AI邮件写作,免费写作助手",
        "slug": "free-ai-writing-tools",
        "sections": [
            ("为什么需要AI写作工具？", "在信息爆炸的时代，写作能力变得越来越重要。但不是每个人都有出色的写作天赋，这时候AI写作工具就能帮上大忙。AI写作工具可以帮你：快速生成文章框架、优化文案措辞、检查语法错误、翻译多语言内容。"),
            ("1. NextTool AI文案助手", "NextTool的AI文案助手是最推荐的免费写作工具。它支持多种写作场景：小红书种草文案、公众号文章、产品描述、邮件撰写。最重要的是完全免费，不需要注册！网址：lishoulan.github.io/nextool-apps/"),
            ("2. AI邮件写作器", "写邮件总是不知道怎么开头？AI邮件写作器帮你：自动生成专业邮件、支持多种语气（正式/友好/感谢）、10种常见场景模板。商务邮件、求职邮件、感谢信，一键搞定。"),
            ("3. AI论文改写工具", "论文查重率太高？AI改写工具帮你：同义替换降低重复率、保持原意不变、学术风格优化。毕业论文必备神器！"),
            ("4. AI翻译工具", "需要翻译文档？AI翻译比传统翻译更智能：上下文理解更准确、专业术语翻译更地道、支持8种语言互译。"),
            ("5. AI文本摘要", "文章太长没时间看？AI摘要工具帮你：秒级生成文章摘要、提取关键词、保留核心观点。")
        ]
    },
    {
        "title": "AI论文降重方法大全：5种方法帮你顺利通过查重",
        "description": "详细介绍5种AI论文降重方法，包括同义替换、句式变换、段落重组等，帮你轻松通过查重！",
        "keywords": "AI论文降重,论文查重,降重方法,论文改写工具,毕业论文降重",
        "slug": "ai-paper-plagiarism-reduction",
        "sections": [
            ("论文降重为什么重要？", "毕业论文查重是每个毕业生必须面对的关卡。大部分学校要求查重率低于30%，有些甚至要求低于15%。如果查重率过高，轻则修改，重则延期毕业。"),
            ("方法1：AI同义替换", "使用AI工具将原文中的词语替换为同义词，这是最基础的降重方法。NextTool的AI论文改写工具可以自动完成同义替换，同时保持原意不变。"),
            ("方法2：句式变换", "将主动句改为被动句，或者调整句子结构。例如：'AI技术改变了写作方式' → '写作方式被AI技术所改变'。"),
            ("方法3：段落重组", "将段落中的句子顺序调整，或者将一个长段落拆分为多个短段落。这种方法可以有效降低连续重复的字数。"),
            ("方法4：引用规范", "确保所有引用的内容都正确标注了出处。规范的引用不会被计入查重率。使用正确的引用格式（APA、MLA等）。"),
            ("方法5：AI智能改写", "最推荐的方法！使用NextTool的AI论文改写工具，一键完成以上所有操作。工具会自动：识别重复内容、智能替换同义词、优化句式结构、保持学术风格。")
        ]
    },
    {
        "title": "在线PDF工具哪个好用？2026年最全PDF工具对比",
        "description": "对比2026年最好用的在线PDF工具，包括PDF合并、拆分、压缩、转图片等功能，帮你找到最适合的PDF工具！",
        "keywords": "在线PDF工具,PDF合并,PDF压缩,PDF转图片,免费PDF工具",
        "slug": "online-pdf-tools-comparison",
        "sections": [
            ("为什么需要在线PDF工具？", "PDF是最常用的文档格式之一，但PDF文件不容易编辑。在线PDF工具可以帮你：合并多个PDF、拆分PDF页面、压缩PDF文件大小、将PDF转为图片。不需要安装软件，打开浏览器就能用。"),
            ("NextTool PDF工具箱", "NextTool提供一站式PDF解决方案：PDF合并、PDF拆分、PDF压缩、PDF转图片、图片转PDF、PDF加水印。6大功能全免费，本地处理隐私安全。"),
            ("与其他工具对比", "相比Smallpdf、iLovePDF等工具，NextTool的优势：完全免费无限制、不需要注册、本地处理不上传服务器、中文界面更友好。"),
            ("使用方法", "3步完成PDF操作：1. 打开NextTool PDF工具箱；2. 上传PDF文件；3. 选择操作并下载结果。就这么简单！"),
            ("常见问题", "Q: 文件安全吗？A: 所有文件在浏览器本地处理，不会上传到服务器。Q: 支持多大的文件？A: 取决于你的浏览器内存，一般50MB以内没问题。Q: 需要付费吗？A: 完全免费，没有隐藏收费。")
        ]
    },
    {
        "title": "免费AI翻译工具对比：哪个翻译最准确？",
        "description": "对比5款免费AI翻译工具的翻译质量，包括DeepL、百度翻译、Google翻译等，帮你找到最准确的翻译工具！",
        "keywords": "免费AI翻译工具,翻译工具对比,最准确的翻译,AI翻译推荐,多语言翻译",
        "slug": "free-ai-translation-comparison",
        "sections": [
            ("AI翻译 vs 传统翻译", "AI翻译相比传统机器翻译有质的飞跃：理解上下文、专业术语更准确、翻译更自然流畅。特别是中英文翻译，AI翻译的质量已经接近人工翻译水平。"),
            ("1. NextTool AI翻译", "基于先进大语言模型的翻译工具，支持8种语言互译。特点：上下文理解能力强、支持学术/商务/口语多种风格、完全免费使用。"),
            ("2. DeepL翻译", "欧洲最受欢迎的翻译工具，翻译质量高。但免费版有字数限制，长文档需要付费。"),
            ("3. Google翻译", "最老牌的翻译工具，支持100+语言。但翻译质量一般，特别是中英文翻译经常出现语法错误。"),
            ("4. 百度翻译", "国内使用最方便的翻译工具，支持中英日韩等语言。翻译质量中等，专业术语翻译不够准确。"),
            ("5. 有道翻译", "网易旗下的翻译工具，词典功能强大。但AI翻译能力不如NextTool和DeepL。")
        ]
    },
    {
        "title": "程序员必备！10个免费在线开发工具推荐",
        "description": "推荐10个程序员必备的免费在线开发工具，包括JSON格式化、正则测试、Base64编解码等，提升开发效率！",
        "keywords": "程序员在线工具,JSON格式化,正则测试,免费开发工具,开发者工具",
        "slug": "must-have-developer-tools",
        "sections": [
            ("为什么需要在线开发工具？", "日常开发中，有些操作用代码写太麻烦，用软件又太重。在线开发工具完美解决这个问题：打开浏览器就能用、不需要安装、跨平台兼容。"),
            ("1. JSON格式化工具", "后端返回的JSON数据格式乱了？一键美化、压缩、验证语法。NextTool的JSON格式化还支持树形视图和JSON Path查询。"),
            ("2. 正则表达式测试器", "写正则最痛苦的是调试。在线正则测试器可以：实时匹配预览、分组高亮显示、常用正则模板库。"),
            ("3. Base64编解码", "接口调试经常需要Base64编解码。支持文本和图片互转，开发者必备。"),
            ("4. URL编解码工具", "处理URL参数、OAuth回调URL、API签名计算时必备。"),
            ("5. 时间戳转换", "开发中经常需要时间戳和日期互转，这个工具支持秒级和毫秒级。"),
            ("6. AI代码解释器", "看不懂别人的代码？AI逐行解释，支持30+编程语言。"),
            ("7. Markdown编辑器", "写README、写文档、写博客，实时预览+导出。"),
            ("8. 颜色选择器", "HEX/RGB/HSL转换、CSS渐变生成，前端开发必备。"),
            ("9. 密码生成器", "生成安全随机密码，自定义规则+强度检测。"),
            ("10. 二维码生成器", "生成QR Code，自定义颜色尺寸，支持Logo嵌入。")
        ]
    },
    {
        "title": "AI简历优化技巧：让你的简历通过率提升80%",
        "description": "分享AI简历优化的5个技巧，包括关键词优化、经历润色、格式调整等，帮你拿到更多面试机会！",
        "keywords": "AI简历优化,简历技巧,求职简历,简历关键词,面试通过率",
        "slug": "ai-resume-optimization-tips",
        "sections": [
            ("为什么简历需要优化？", "HR平均只花6秒看一份简历。如果你的简历不能在6秒内吸引HR的注意，就会被淘汰。AI简历优化可以帮你：突出核心优势、匹配岗位关键词、优化排版结构。"),
            ("技巧1：关键词匹配", "很多公司使用ATS（申请人追踪系统）筛选简历。ATS会扫描简历中的关键词，如果你的简历缺少关键词，就会被自动淘汰。NextTool的AI简历优化器可以自动提取JD中的关键词并优化你的简历。"),
            ("技巧2：量化成果", "不要只写'负责项目管理'，要写'管理5人团队，项目按时交付率提升30%'。量化的成果比模糊的描述更有说服力。"),
            ("技巧3：优化措辞", "将'参与了项目开发'改为'主导核心模块开发，代码质量评分A+'。AI工具可以帮你自动优化措辞，让经历更亮眼。"),
            ("技巧4：调整结构", "将最重要的经历放在最前面。HR看简历是从上到下的，第一屏的内容最重要。"),
            ("技巧5：针对性修改", "每投一个岗位，都应该根据JD调整简历。AI简历优化器可以一键生成不同版本的简历。")
        ]
    },
    {
        "title": "免费AI PPT生成器：3分钟做出专业演示文稿",
        "description": "介绍免费AI PPT生成器的使用方法，输入主题自动生成专业PPT，3分钟搞定演示文稿！",
        "keywords": "免费AI PPT生成器,PPT自动生成,AI做PPT,演示文稿生成,免费PPT工具",
        "slug": "free-ai-ppt-generator-guide",
        "sections": [
            ("AI PPT生成器是什么？", "AI PPT生成器是一种利用人工智能技术，根据用户输入的主题自动生成演示文稿的工具。你只需要输入一个主题，AI就会自动：生成PPT大纲、设计页面布局、填充内容文字、选择配色方案。"),
            ("NextTool AI PPT生成器", "NextTool提供免费的AI PPT生成器，特点：完全免费使用、不需要注册、3分钟出完整PPT、支持多种风格模板。"),
            ("使用步骤", "3步生成PPT：1. 打开NextTool AI PPT生成器；2. 输入你的演示主题（如'2026年营销策略'）；3. 点击生成，等待3分钟。就这么简单！"),
            ("适用场景", "AI PPT生成器适用于：课堂展示、工作汇报、项目提案、产品介绍、培训课件。任何需要快速制作PPT的场景都适用。"),
            ("常见问题", "Q: 生成的PPT可以编辑吗？A: 可以，生成后可以自由修改内容和样式。Q: 支持导出什么格式？A: 支持PPTX和PDF格式。Q: 有模板选择吗？A: 支持商务、简约、创意等多种风格。")
        ]
    },
    {
        "title": "AI合同生成器使用指南：10分钟生成专业法律文书",
        "description": "详细介绍AI合同生成器的使用方法，支持12种合同类型，10分钟生成律师审核级质量的法律文书！",
        "keywords": "AI合同生成器,法律文书生成,合同模板,免费合同工具,在线合同制作",
        "slug": "ai-contract-generator-guide",
        "sections": [
            ("为什么需要AI合同生成器？", "请律师起草合同动辄几千块，而且需要等待几天。AI合同生成器可以在10分钟内生成专业合同，而且完全免费。适用于：劳动合同、租赁合同、服务协议、保密协议等12种常见合同类型。"),
            ("NextTool AI合同生成器", "特点：支持12种合同类型、律师审核级质量、一键导出Word、完全免费使用。"),
            ("使用方法", "4步生成合同：1. 选择合同类型；2. 填写基本信息（甲乙方、金额等）；3. AI自动生成合同内容；4. 检查并导出Word。"),
            ("注意事项", "AI生成的合同仅供参考，重要合同建议请专业律师审核。但作为初稿，AI合同已经能覆盖大部分常见条款。"),
            ("适用人群", "创业者、小企业主、自由职业者、房东/租客。任何需要快速起草合同的人都能用上。")
        ]
    },
    {
        "title": "学生党免费工具推荐：论文、简历、PPT一站搞定",
        "description": "为学生党推荐15个免费在线工具，覆盖论文写作、简历制作、PPT生成、翻译等场景，全部免费！",
        "keywords": "学生免费工具,论文工具,简历制作,PPT生成,学生党必备",
        "slug": "student-free-tools-guide",
        "sections": [
            ("学生党最需要的工具", "大学四年，论文、简历、PPT、翻译……各种需求层出不穷。但大部分好用的工具都要收费。今天给大家推荐15个完全免费的在线工具！"),
            ("论文相关工具", "AI论文改写 - 降低查重率、AI翻译 - 翻译英文文献、AI摘要 - 快速阅读论文、字数统计 - 控制论文字数。"),
            ("求职相关工具", "AI简历优化 - 让简历更亮眼、AI邮件写作 - 写求职邮件、AI合同生成 - 签劳动合同前看看。"),
            ("学习相关工具", "AI代码解释器 - 看懂课程代码、Markdown编辑器 - 写笔记、JSON格式化 - 做项目调试。"),
            ("日常工具", "PDF工具箱 - 合并拆分压缩、图片压缩 - 压缩作业图片、密码生成器 - 生成安全密码、二维码生成器 - 做项目展示。"),
            ("所有工具都在这里", "NextTool免费AI工具箱：lishoulan.github.io/nextool-apps/，25+种工具全部免费，不用注册，打开就用！")
        ]
    },
    {
        "title": "打工人效率提升：5个免费AI工具让你准时下班",
        "description": "分享5个免费AI工具，帮助打工人提升工作效率，每天少加班2小时，准时下班不是梦！",
        "keywords": "打工人效率工具,AI效率提升,免费AI工具,准时下班,工作效率",
        "slug": "worker-efficiency-ai-tools",
        "sections": [
            ("打工人的痛点", "每天加班到9点？工作效率低？其实不是你能力不行，而是工具没选对。好的工具能让你事半功倍。"),
            ("1. AI文案助手 - 写周报神器", "以前写周报要30分钟回忆这周做了什么，现在用AI文案助手3分钟搞定。输入关键词，AI自动生成格式工整的周报。"),
            ("2. AI邮件写作 - 沟通效率翻倍", "给客户写邮件不知道怎么措辞？AI邮件写作器帮你：自动生成专业邮件、支持多种语气、10种场景模板。"),
            ("3. AI翻译工具 - 看英文文档不求人", "英文文档看不懂？AI翻译比百度翻译更智能，上下文理解更准确，专业术语翻译更地道。"),
            ("4. PDF工具箱 - 处理文档一步到位", "PDF合并、拆分、压缩，一个工具全搞定。不需要安装软件，在线直接操作。"),
            ("5. AI合同生成 - 10分钟出合同", "需要起草合同？AI合同生成器10分钟搞定，律师审核级质量，支持12种合同类型。"),
            ("开始使用", "所有工具都在NextTool免费AI工具箱：lishoulan.github.io/nextool-apps/，完全免费，不用注册！")
        ]
    }
]

def generate_article():
    """从模板中随机选择并生成文章"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 随机选择模板
    template = random.choice(ARTICLE_TEMPLATES)
    
    title = template["title"]
    description = template["description"]
    keywords = template["keywords"]
    slug = template["slug"]
    sections = template["sections"]
    
    print(f"📋 Selected topic: {title}")
    
    # 生成HTML
    sections_html = ""
    for heading, content in sections:
        sections_html += f"""
        <h2>{heading}</h2>
        <p>{content}</p>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | NextTool博客</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="{SITE_URL}blog/{today}-{slug}.html">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{SITE_URL}blog/{today}-{slug}.html">
    <meta property="og:type" content="article">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title}",
      "description": "{description}",
      "url": "{SITE_URL}blog/{today}-{slug}.html",
      "datePublished": "{today}",
      "author": {{
        "@type": "Organization",
        "name": "NextTool"
      }}
    }}
    </script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0c29; color: #e0e0e0; line-height: 1.8; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem 1.5rem; }}
        h1 {{ font-size: 1.8rem; margin-bottom: 1rem; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        h2 {{ font-size: 1.4rem; margin: 2rem 0 1rem; color: #00d2ff; border-bottom: 1px solid rgba(0,210,255,0.2); padding-bottom: 0.5rem; }}
        p {{ margin-bottom: 1rem; }}
        a {{ color: #00d2ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .back-link {{ display: inline-block; margin-bottom: 1.5rem; color: #aaa; }}
        .back-link:hover {{ color: #00d2ff; }}
        .cta {{ display: inline-block; background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: #fff; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 1rem 0; }}
        .cta:hover {{ text-decoration: none; transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,210,255,0.3); }}
        footer {{ text-align: center; padding: 2rem 0; color: #555; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 3rem; }}
    </style>
</head>
<body>
    <div class="container">
        <a class="back-link" href="/nextool-apps/blog/">&larr; 返回博客</a>
        <h1>{title}</h1>
        {sections_html}
        <div style="text-align:center; margin: 2rem 0;">
            <a class="cta" href="/nextool-apps/">立即使用NextTool免费AI工具箱</a>
        </div>
    </div>
    <footer>
        <p>&copy; 2026 NextTool - 免费AI在线工具箱 | <a href="/nextool-apps/">首页</a> | <a href="/nextool-apps/blog/">博客</a></p>
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
    
    # 写入文件
    filename = f"blog/{today}-{slug}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Article generated: {filename}")
    return filename, f"{SITE_URL}blog/{today}-{slug}.html"

def push_to_indexnow(url):
    """通过IndexNow推送URL到搜索引擎"""
    import urllib.request
    import urllib.error
    
    payload = {
        "host": "lishoulan.github.io",
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_URL}{INDEXNOW_KEY}.txt",
        "urlList": [url]
    }
    
    for endpoint in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow", "https://yandex.com/indexnow"]:
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=30)
            print(f"  IndexNow ({endpoint.split('//')[1].split('/')[0]}): {resp.status}")
        except urllib.error.HTTPError as e:
            print(f"  IndexNow ({endpoint.split('//')[1].split('/')[0]}): HTTP {e.code}")
        except Exception as e:
            print(f"  IndexNow ({endpoint.split('//')[1].split('/')[0]}): {e}")

if __name__ == "__main__":
    print(f"🤖 Daily SEO Content Generator - {datetime.now().strftime('%Y-%m-%d')}")
    
    filename, url = generate_article()
    
    print(f"\n📡 Pushing to search engines...")
    push_to_indexnow(url)
    
    print(f"\n✅ Done! Article: {filename}")
    print(f"🔗 URL: {url}")
