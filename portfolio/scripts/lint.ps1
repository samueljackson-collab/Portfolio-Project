#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

ruff check (Join-Path $PSScriptRoot '..' 'projects' 'backend' 'app') (Join-Path $PSScriptRoot '..' 'projects' 'backend' 'tests')
npm run lint --prefix (Join-Path $PSScriptRoot '..' 'projects' 'frontend')
