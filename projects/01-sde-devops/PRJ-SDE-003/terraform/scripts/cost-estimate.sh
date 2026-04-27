#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT=${1:-dev}
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(dirname "$SCRIPT_DIR")
ENV_DIR="$ROOT_DIR/environments/${ENVIRONMENT}"

if [[ ! -d "$ENV_DIR" ]]; then
  echo "Unknown environment: ${ENVIRONMENT}" >&2
  exit 1
fi

echo "Run your preferred cost estimation tool (e.g., infracost) against ${ENV_DIR}."
