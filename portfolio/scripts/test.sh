#!/usr/bin/env bash
set -euo pipefail

pytest --cov="$(dirname "$0")/../projects/backend/app" --cov-report=term-missing --cov-fail-under=80 "$(dirname "$0")/../projects/backend/tests"
npm test --prefix "$(dirname "$0")/../projects/frontend" -- --run
