$OutputDir = "artifacts"
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$ArchiveName = "portfolio-monorepo-$(Get-Date -Format 'yyyyMMddHHmmss').zip"

Compress-Archive -Path backend, frontend, e2e-tests, infra, monitoring, docs, README.md, CHANGELOG.md, LICENSE `
    -DestinationPath (Join-Path $OutputDir $ArchiveName) `
    -Force

Write-Host "Created $ArchiveName in $OutputDir"
