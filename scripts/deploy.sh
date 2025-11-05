#!/usr/bin/env bash
# Local helper wrapper to run Terraform safely (fmt -> init -> plan -> apply interactive)
# Usage: ./scripts/deploy.sh [workspace] [auto-approve]
set -euo pipefail

WORKSPACE="${1:-default}"
AUTO_APPROVE="${2:-false}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}/terraform"

echo "Formatting Terraform files..."
terraform fmt -recursive

echo "Initializing Terraform (will use backend config)..."
terraform init -input=false

echo "Selecting workspace: ${WORKSPACE}"
if terraform workspace list | grep -q "${WORKSPACE}"; then
  terraform workspace select "${WORKSPACE}"
else
  terraform workspace new "${WORKSPACE}"
fi

echo "Validating configuration..."
terraform validate

echo "Planning..."
terraform plan -out=plan.tfplan

if [ "${AUTO_APPROVE}" = "true" ]; then
  echo "Applying plan (auto-approve)..."
  terraform apply -input=false -auto-approve plan.tfplan
else
  echo "To apply: terraform apply -input=false plan.tfplan"
fi
