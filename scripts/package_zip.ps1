$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Join-Path $RootDir '..'
$OutputDir = Join-Path $RootDir 'reports'
$ArchiveName = "portfolio-monorepo-$(Get-Date -Format yyyyMMdd).zip"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$items = Get-ChildItem -Path $RootDir -Recurse -File |
    Where-Object { $_.FullName -notmatch 'node_modules|\.terraform|__pycache__|\.git' }

$zipPath = Join-Path $OutputDir $ArchiveName
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path $items.FullName -DestinationPath $zipPath

$hash = Get-FileHash -Algorithm SHA256 -Path $zipPath
"$($hash.Hash)  $ArchiveName" | Set-Content -Path (Join-Path $OutputDir "$ArchiveName.sha256")

Write-Host "Package created at $zipPath"
