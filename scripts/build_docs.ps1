param(
    [string]$DocsDir = "docs",
    [string]$OutputDir = "build/docs",
    [ValidateSet("html", "pdf")][string]$Format = "html",
    [string]$Title = "Portfolio Research Docs"
)

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Host "Pandoc is required to bundle documentation." -ForegroundColor Yellow
    Write-Host "Download: https://pandoc.org/installing.html" -ForegroundColor Yellow
    Write-Host "winget install --id=JohnMacFarlane.Pandoc" -ForegroundColor Yellow
    exit 1
}

$docFiles = Get-ChildItem -Path $DocsDir -Filter '*.md' -Recurse | Sort-Object FullName

if (-not $docFiles) {
    Write-Host "No Markdown files found under $DocsDir. Nothing to bundle." -ForegroundColor Cyan
    exit 0
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$outputFile = Join-Path $OutputDir "research-docs.$Format"

$pandocArgs = @()
foreach ($file in $docFiles) {
    $pandocArgs += $file.FullName
}
$pandocArgs += @('--from', 'markdown', '--toc', '--metadata', "title=$Title", '-o', $outputFile)

& pandoc @pandocArgs

Write-Host "Bundled documentation saved to $outputFile" -ForegroundColor Green
