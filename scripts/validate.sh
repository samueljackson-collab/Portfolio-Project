#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

pushd "$PROJECT_ROOT/infrastructure/terraform" >/dev/null

echo "[validate] Running terraform fmt check..."
terraform fmt -check -recursive

echo "[validate] Initializing Terraform without backend..."
terraform init -backend=false

echo "[validate] Running terraform validate..."
terraform validate

if command -v tflint >/dev/null 2>&1; then
  echo "[validate] Running tflint..."
  tflint --init
  tflint
else
  echo "[validate] tflint not installed; skipping lint checks." >&2
fi

popd >/dev/null

echo "[validate] Validation complete."
