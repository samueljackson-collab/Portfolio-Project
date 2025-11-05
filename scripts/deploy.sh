#!/usr/bin/env bash
# Local helper wrapper to run Terraform safely with proper backend configuration
#
# Usage: ./scripts/deploy.sh [workspace] [auto-approve]
#
# Examples:
#   # Interactive mode (default workspace)
#   ./scripts/deploy.sh
#
#   # Use dev workspace
#   ./scripts/deploy.sh dev
#
#   # Auto-approve in dev workspace (use with caution!)
#   ./scripts/deploy.sh dev true
#
# Backend Configuration:
#   This script looks for backend.hcl in the terraform directory.
#   If not found, you'll need to provide backend config via CLI flags or environment variables.
#   See terraform/backend.tf for details.

set -euo pipefail

WORKSPACE="${1:-default}"
AUTO_APPROVE="${2:-false}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}/terraform"

echo "=========================================="
echo "Terraform Deployment"
echo "=========================================="
echo "Workspace:    ${WORKSPACE}"
echo "Auto-approve: ${AUTO_APPROVE}"
echo "=========================================="
echo ""

echo "→ Formatting Terraform files..."
terraform fmt -recursive

echo ""
echo "→ Initializing Terraform..."
if [ -f "backend.hcl" ]; then
  echo "  (Using backend.hcl for configuration)"
  terraform init -backend-config=backend.hcl -input=false
else
  echo "  (No backend.hcl found - using CLI args or environment variables)"
  terraform init -input=false
fi

echo ""
echo "→ Selecting workspace: ${WORKSPACE}"
if terraform workspace list | grep -q "^\*\?\s*${WORKSPACE}\$"; then
  terraform workspace select "${WORKSPACE}"
else
  terraform workspace new "${WORKSPACE}"
fi

echo ""
echo "→ Validating configuration..."
terraform validate

echo ""
echo "→ Planning changes..."
terraform plan -out=plan.tfplan

echo ""
if [ "${AUTO_APPROVE}" = "true" ]; then
  echo "→ Applying plan (auto-approve enabled)..."
  terraform apply -input=false -auto-approve plan.tfplan
  echo ""
  echo "✓ Apply complete!"
else
  echo "=========================================="
  echo "Plan saved to: plan.tfplan"
  echo "=========================================="
  echo ""
  echo "To apply these changes, run:"
  echo "  cd terraform && terraform apply -input=false plan.tfplan"
  echo ""
fi