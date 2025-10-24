#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

pushd "$PROJECT_ROOT/infrastructure/terraform" >/dev/null

echo "[destroy] Initializing Terraform..."
terraform init

echo "[destroy] Destroying infrastructure..."
terraform destroy

popd >/dev/null

echo "[destroy] Destroy complete."
