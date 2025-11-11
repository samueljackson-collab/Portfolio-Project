#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

pytest --cov=projects/backend/app --cov-report=term-missing projects/backend/app/tests
Push-Location projects/frontend
try {
    npm run test
}
finally {
    Pop-Location
}
