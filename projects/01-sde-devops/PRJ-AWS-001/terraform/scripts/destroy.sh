#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
ROOT_DIR="$(cd -- "$(dirname "$0")/.." && pwd)"
ENV_DIR="$ROOT_DIR/environments/$ENVIRONMENT"

if [[ ! -d "$ENV_DIR" ]]; then
  echo "Unknown environment: $ENVIRONMENT" >&2
  exit 1
fi

read -rp "Destroy environment '$ENVIRONMENT'? (y/N) " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Aborting."
  exit 0
fi

pushd "$ENV_DIR" >/dev/null
terraform init -upgrade
terraform destroy -auto-approve
popd >/dev/null
