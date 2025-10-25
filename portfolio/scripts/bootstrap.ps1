#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

python -m pip install --upgrade pip
python -m pip install -r (Join-Path $PSScriptRoot '..' 'requirements.txt')
npm install --prefix (Join-Path $PSScriptRoot '..' 'projects' 'frontend')
