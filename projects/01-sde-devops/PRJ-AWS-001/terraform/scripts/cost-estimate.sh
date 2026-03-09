#!/usr/bin/env bash
set -euo pipefail

if ! command -v infracost >/dev/null; then
  echo "infracost CLI not installed. Install from https://www.infracost.io/docs/" >&2
  exit 1
fi

ENVIRONMENT="${1:-dev}"
ROOT_DIR="$(cd -- "$(dirname "$0")/.." && pwd)"
ENV_DIR="$ROOT_DIR/environments/$ENVIRONMENT"
OUTPUT_FILE="infracost-${ENVIRONMENT}.json"

pushd "$ENV_DIR" >/dev/null
terraform init -backend=false
infracost breakdown --path . --format json --out-file "$OUTPUT_FILE"
echo "Cost estimate written to $ENV_DIR/$OUTPUT_FILE"
popd >/dev/null
