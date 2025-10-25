#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

pytest --cov=(Join-Path $PSScriptRoot '..' 'projects' 'backend' 'app') --cov-report=term-missing --cov-fail-under=80 (Join-Path $PSScriptRoot '..' 'projects' 'backend' 'tests')
npm test --prefix (Join-Path $PSScriptRoot '..' 'projects' 'frontend') -- --run
