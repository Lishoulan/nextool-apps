$baseDir = "d:\100\nextool-apps"

Write-Output "=== Checking related-tools.js ==="
$allPages = @(
    'ai-code-explainer','ai-contract-generator','ai-email-writer','ai-paper-rewriter',
    'ai-ppt-generator','ai-resume-optimizer','ai-summarizer','ai-translator',
    'base64-tool','calculator','color-picker','image-compressor','json-formatter',
    'markdown-editor','password-generator','pdf-toolkit','qr-generator','regex-tester',
    'timestamp-tool','url-tool','word-counter'
)
foreach ($slug in $allPages) {
    $file = "${baseDir}\${slug}\index.html"
    $content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
    $rtCount = ([regex]::Matches($content, 'related-tools\.js')).Count
    $hasCorrectSlug = $content -match "data-current=""${slug}"""
    $status = if ($rtCount -eq 1 -and $hasCorrectSlug) { "OK" } else { "ISSUE" }
    Write-Output "${slug} | related-tools=${rtCount} correct-slug=${hasCorrectSlug} => ${status}"
}

Write-Output ""
Write-Output "=== Checking HowTo JSON-LD ==="
$aiPages = @('ai-ppt-generator','ai-resume-optimizer','ai-contract-generator','ai-email-writer','ai-paper-rewriter','ai-translator','ai-code-explainer','ai-summarizer')
foreach ($slug in $aiPages) {
    $file = "${baseDir}\${slug}\index.html"
    $content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
    $hasHowTo = $content -match '"@type"\s*:\s*"HowTo"'
    Write-Output "${slug} | HowTo=${hasHowTo}"
}
