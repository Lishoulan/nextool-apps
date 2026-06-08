$baseDir = "d:\100\nextool-apps"

$howToSchemas = @{
    'ai-ppt-generator' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI生成专业PPT",
  "description": "使用NexTool AI PPT生成器，输入主题即可一键生成专业演示文稿。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI PPT生成器",
      "text": "访问NexTool AI PPT生成器页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "输入演示主题",
      "text": "在主题输入框中填写你的演示主题，例如"年度工作总结"或"产品发布会"，并选择幻灯片数量和风格。"
    },
    {
      "@type": "HowToStep",
      "name": "点击生成PPT",
      "text": "点击"生成PPT"按钮，AI将根据主题自动生成包含标题页、内容页和结尾页的完整幻灯片。"
    },
    {
      "@type": "HowToStep",
      "name": "导出并使用",
      "text": "预览生成结果后，点击"导出幻灯片"下载HTML格式文件，或点击"复制内容"获取文本。"
    }
  ]
}
</script>
'@
    'ai-resume-optimizer' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI优化简历",
  "description": "使用NexTool AI简历优化器，智能润色简历内容，匹配岗位关键词，提升面试邀约率。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI简历优化器",
      "text": "访问NexTool AI简历优化器页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "输入简历内容和目标岗位",
      "text": "在输入框中粘贴你的简历内容，并填写目标岗位名称，例如"高级前端工程师"。"
    },
    {
      "@type": "HowToStep",
      "name": "点击一键优化",
      "text": "点击"一键优化简历"按钮，AI将自动优化措辞、突出亮点、添加行业关键词。"
    },
    {
      "@type": "HowToStep",
      "name": "复制优化结果",
      "text": "对比原始简历和优化后简历，点击"复制优化结果"按钮获取优化后的简历文本。"
    }
  ]
}
</script>
'@
    'ai-contract-generator' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI生成合同",
  "description": "使用NexTool AI合同生成器，选择合同类型并填写信息，AI自动生成专业法律文书。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI合同生成器",
      "text": "访问NexTool AI合同生成器页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "选择合同类型并填写信息",
      "text": "从12种合同类型中选择需要的类型，如劳动合同、租赁合同等，然后填写甲乙方信息和合同条款。"
    },
    {
      "@type": "HowToStep",
      "name": "点击生成合同",
      "text": "点击"生成专业合同"按钮，AI将根据填写的信息自动生成格式规范、条款完整的合同文本。"
    },
    {
      "@type": "HowToStep",
      "name": "复制或下载合同",
      "text": "生成完成后，点击"复制文本"或"下载文件"按钮获取合同内容。"
    }
  ]
}
</script>
'@
    'ai-email-writer' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI写邮件",
  "description": "使用NexTool AI邮件助手，选择场景和语气，AI自动撰写专业邮件。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI邮件助手",
      "text": "访问NexTool AI邮件助手页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "选择场景并描述内容",
      "text": "选择邮件场景（如商务合作、求职应聘等），选择语气风格，并简要描述你想表达的内容。"
    },
    {
      "@type": "HowToStep",
      "name": "点击撰写邮件",
      "text": "点击"撰写邮件"按钮，AI将自动生成包含邮件主题和正文的完整专业邮件。"
    },
    {
      "@type": "HowToStep",
      "name": "复制或编辑邮件",
      "text": "预览生成结果后，可一键复制全文，或切换到编辑模式进行修改后使用。"
    }
  ]
}
</script>
'@
    'ai-paper-rewriter' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI降低论文查重率",
  "description": "使用NexTool论文降重助手，AI智能改写论文段落，有效降低查重率同时保持原意。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开论文降重助手",
      "text": "访问NexTool论文降重助手页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "输入论文段落",
      "text": "在输入框中粘贴需要降重的论文段落，选择改写强度（轻度、中度、深度）和目标相似率。"
    },
    {
      "@type": "HowToStep",
      "name": "点击开始降重",
      "text": "点击"开始降重"按钮，AI将智能改写文本，在保持学术含义不变的前提下降低与原文的相似度。"
    },
    {
      "@type": "HowToStep",
      "name": "复制降重结果",
      "text": "查看改写结果和对比视图，确认无误后点击"一键复制"获取改写后的文本。"
    }
  ]
}
</script>
'@
    'ai-translator' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI翻译文本",
  "description": "使用NexTool AI翻译工具，支持8种语言互译，可选择日常、商务、学术等多种翻译风格。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI翻译工具",
      "text": "访问NexTool AI翻译页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "设置语言和风格",
      "text": "选择源语言和目标语言，选择翻译风格（日常、商务、学术、文学），然后输入要翻译的文本。"
    },
    {
      "@type": "HowToStep",
      "name": "点击翻译",
      "text": "点击"翻译"按钮，AI将根据所选风格生成自然流畅的翻译结果。"
    },
    {
      "@type": "HowToStep",
      "name": "复制翻译结果",
      "text": "翻译完成后，点击"复制结果"按钮获取翻译文本。"
    }
  ]
}
</script>
'@
    'ai-code-explainer' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI解释代码",
  "description": "使用NexTool AI代码解释器，粘贴代码即可获得逐行解释和优化建议。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI代码解释器",
      "text": "访问NexTool AI代码解释器页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "输入代码并选择语言",
      "text": "在代码输入框中粘贴你的代码，选择编程语言和解释深度（小白友好、进阶、专家）。"
    },
    {
      "@type": "HowToStep",
      "name": "点击解释代码",
      "text": "点击"解释代码"按钮，AI将逐行分析代码逻辑，生成代码概要和详细解释。"
    },
    {
      "@type": "HowToStep",
      "name": "复制解释结果",
      "text": "查看代码概要和逐行解释后，点击"复制解释"按钮获取分析结果。"
    }
  ]
}
</script>
'@
    'ai-summarizer' = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何使用AI生成文本摘要",
  "description": "使用NexTool AI摘要工具，基于TextRank算法快速提取文章核心内容，完全免费无需注册。",
  "step": [
    {
      "@type": "HowToStep",
      "name": "打开AI摘要工具",
      "text": "访问NexTool AI摘要工具页面，进入工具主界面。"
    },
    {
      "@type": "HowToStep",
      "name": "粘贴文本并选择长度",
      "text": "在输入框中粘贴文章、论文或新闻等文本内容，选择摘要长度（简短、适中、详细）。"
    },
    {
      "@type": "HowToStep",
      "name": "点击生成摘要",
      "text": "点击"生成摘要"按钮，TextRank算法将自动提取关键句子生成摘要，同时提取关键词。"
    },
    {
      "@type": "HowToStep",
      "name": "复制摘要结果",
      "text": "查看摘要结果和关键词后，点击"复制摘要"按钮获取摘要文本。"
    }
  ]
}
</script>
'@
}

foreach ($entry in $howToSchemas.GetEnumerator()) {
    $slug = $entry.Key
    $howToSchema = $entry.Value
    $file = "$baseDir\$slug\index.html"
    $content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

    # Check if HowTo schema already exists
    if ($content -match '"@type":\s*"HowTo"') {
        Write-Output "SKIP (HowTo already exists): $slug"
        continue
    }

    # Find the last </head> and insert before it
    # We need to insert the HowTo schema before </head>
    $headCloseIndex = $content.LastIndexOf('</head>')
    if ($headCloseIndex -eq -1) {
        Write-Output "ERROR (no </head> found): $slug"
        continue
    }

    $newContent = $content.Substring(0, $headCloseIndex) + $howToSchema + [Environment]::NewLine + $content.Substring($headCloseIndex)

    [System.IO.File]::WriteAllText($file, $newContent, [System.Text.Encoding]::UTF8)
    Write-Output "DONE: $slug"
}
