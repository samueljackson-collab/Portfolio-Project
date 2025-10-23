#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
ENV_DIR="$ROOT_DIR/infra/environments/prod"

pushd "$ENV_DIR" >/dev/null

echo "Running terraform fmt check..."
if ! command -v terraform >/dev/null 2>&1; then
  echo "Error: terraform is not installed or not in PATH." >&2
  exit 1
fi

terraform fmt -check

echo "Initializing terraform (backend disabled)..."
terraform init -backend=false -input=false

echo "Validating configuration..."
terraform validate

if command -v tflint >/dev/null 2>&1; then
  echo "Running tflint..."
  tflint --init >/dev/null
  tflint
else
  echo "Warning: tflint not installed; skipping lint." >&2
fi

if command -v tfsec >/dev/null 2>&1; then
  echo "Running tfsec..."
  tfsec .
else
  echo "Warning: tfsec not installed; skipping security scan." >&2
fi

popd >/dev/null

echo "All integration checks completed successfully."

