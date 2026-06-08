$baseDir = "d:\100\nextool-apps"
$pages = @(
    'ai-code-explainer',
    'ai-contract-generator',
    'ai-email-writer',
    'ai-paper-rewriter',
    'ai-ppt-generator',
    'ai-resume-optimizer',
    'ai-summarizer',
    'ai-translator',
    'base64-tool',
    'calculator',
    'color-picker',
    'image-compressor',
    'json-formatter',
    'markdown-editor',
    'password-generator',
    'pdf-toolkit',
    'qr-generator',
    'regex-tester',
    'timestamp-tool',
    'url-tool',
    'word-counter'
)

foreach ($slug in $pages) {
    $file = "$baseDir\$slug\index.html"
    $content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

    # Check if related-tools.js already exists
    if ($content -match 'related-tools\.js') {
        Write-Output "SKIP (already exists): $slug"
        continue
    }

    # Add script tag before </body>
    $scriptTag = '<script src="../js/related-tools.js" data-current="' + $slug + '"></script>'
    $newContent = $content -replace '</body>', "$scriptTag`n</body>"

    [System.IO.File]::WriteAllText($file, $newContent, [System.Text.Encoding]::UTF8)
    Write-Output "DONE: $slug"
}
