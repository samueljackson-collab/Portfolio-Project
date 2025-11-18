#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$root = (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location (Join-Path $root "..");
$zip = "portfolio-dist.zip"
Write-Host "Packaging repository into $zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path * -DestinationPath $zip -Force -CompressionLevel Optimal -Exclude *.zip,node_modules,.terraform,__pycache__
