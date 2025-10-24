#!/usr/bin/env bash
set -euo pipefail

# Deploy infrastructure via Terraform.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

pushd "$PROJECT_ROOT/infrastructure/terraform" >/dev/null

echo "[deploy] Initializing Terraform..."
terraform init

echo "[deploy] Generating plan..."
terraform plan -out=tfplan

echo "[deploy] Applying infrastructure..."
terraform apply tfplan

rm -f tfplan
popd >/dev/null

echo "[deploy] Deployment complete."
