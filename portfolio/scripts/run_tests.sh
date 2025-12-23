#!/usr/bin/env bash
set -euo pipefail

pytest --cov=projects/backend/app --cov-report=term-missing projects/backend/app/tests
(cd projects/frontend && npm run test)
