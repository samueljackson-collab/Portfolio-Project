#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$root = (Split-Path -Parent $MyInvocation.MyCommand.Path)
$out = Join-Path $root "../docs/_site"
New-Item -ItemType Directory -Path $out -Force | Out-Null
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
  Write-Warning "pandoc is required to build docs. Install pandoc and retry."
  exit 0
}
pandoc (Join-Path $root "../README.md") -o (Join-Path $out "portfolio.html")
