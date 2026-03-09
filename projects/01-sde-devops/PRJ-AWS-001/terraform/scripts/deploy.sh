#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
ROOT_DIR="$(cd -- "$(dirname "$0")/.." && pwd)"
ENV_DIR="$ROOT_DIR/environments/$ENVIRONMENT"

if [[ ! -d "$ENV_DIR" ]]; then
  echo "Unknown environment: $ENVIRONMENT" >&2
  exit 1
fi

pushd "$ENV_DIR" >/dev/null
terraform init -upgrade
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
popd >/dev/null
