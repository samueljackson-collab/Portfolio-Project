#!/usr/bin/env bash
set -euo pipefail

ruff check backend/app
npm run lint --workspace frontend
terraform fmt -recursive infra
