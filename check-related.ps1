$baseDir = "d:\100\nextool-apps"
Get-ChildItem $baseDir -Directory | ForEach-Object {
    $f = Join-Path $_.FullName 'index.html'
    if (Test-Path $f) {
        $c = [System.IO.File]::ReadAllText($f)
        $m = ([regex]::Matches($c, 'related-tools\.js')).Count
        if ($m -gt 0) {
            Write-Output "$($_.Name): $m"
        }
    }
}
