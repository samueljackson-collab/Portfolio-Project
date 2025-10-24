#!/usr/bin/env bash
set -euo pipefail

ruff check "$(dirname "$0")/../projects/backend/app" "$(dirname "$0")/../projects/backend/tests"
npm run lint --prefix "$(dirname "$0")/../projects/frontend"
