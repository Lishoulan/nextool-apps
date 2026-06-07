# NextTool PWA Icon Generator
# Generates PNG icons of various sizes using System.Drawing

Add-Type -AssemblyName System.Drawing

$outputDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sizes = @(72, 96, 128, 144, 152, 192, 384, 512)

# Gradient colors
$colorStart = [System.Drawing.Color]::FromArgb(0x0f, 0x0c, 0x29)  # #0f0c29
$colorEnd   = [System.Drawing.Color]::FromArgb(0x30, 0x2b, 0x63)  # #302b63

foreach ($size in $sizes) {
    $bmp = New-Object System.Drawing.Bitmap($size, $size)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias

    # Rounded rectangle path
    $cornerRadius = [int]($size * 0.18)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $rect = New-Object System.Drawing.Rectangle(0, 0, $size, $size)

    $path.AddArc($rect.X, $rect.Y, $cornerRadius, $cornerRadius, 180, 90)
    $path.AddArc($rect.X + $rect.Width - $cornerRadius, $rect.Y, $cornerRadius, $cornerRadius, 270, 90)
    $path.AddArc($rect.X + $rect.Width - $cornerRadius, $rect.Y + $rect.Height - $cornerRadius, $cornerRadius, $cornerRadius, 0, 90)
    $path.AddArc($rect.X, $rect.Y + $rect.Height - $cornerRadius, $cornerRadius, $cornerRadius, 90, 90)
    $path.CloseFigure()

    # Draw gradient background
    $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        $rect,
        $colorStart,
        $colorEnd,
        [System.Drawing.Drawing2D.LinearGradientMode]::Vertical
    )
    $g.FillPath($brush, $path)

    # Draw white "N" letter
    $fontSize = [int]($size * 0.6)
    $font = New-Object System.Drawing.Font("Segoe UI", $fontSize, [System.Drawing.FontStyle]::Bold)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)

    $textFormat = New-Object System.Drawing.StringFormat
    $textFormat.Alignment = [System.Drawing.StringAlignment]::Center
    $textFormat.LineAlignment = [System.Drawing.StringAlignment]::Center

    $textRect = New-Object System.Drawing.RectangleF(0, 0, $size, $size)
    $g.DrawString("N", $font, $textBrush, $textRect, $textFormat)

    # Save
    $filePath = Join-Path $outputDir "icon-${size}x${size}.png"
    $bmp.Save($filePath, [System.Drawing.Imaging.ImageFormat]::Png)

    Write-Host "Generated: $filePath"

    # Cleanup
    $textBrush.Dispose()
    $font.Dispose()
    $brush.Dispose()
    $path.Dispose()
    $g.Dispose()
    $bmp.Dispose()
}

Write-Host "`nAll icons generated successfully!"
