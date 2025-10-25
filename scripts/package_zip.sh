#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DIST_DIR="$ROOT_DIR/dist"
OUTPUT_NAME=${1:-portfolio_bootstrap_kit.zip}
OUTPUT_PATH="$DIST_DIR/$OUTPUT_NAME"

mkdir -p "$DIST_DIR"

printf 'Creating archive %s\n' "$OUTPUT_PATH"
(
  cd "$ROOT_DIR"
  zip -rq "$OUTPUT_PATH" . \
    -x "*/node_modules/*" \
       "*/__pycache__/*" \
       "*/.terraform/*" \
       "dist/*" \
       ".git/*"
)

printf 'Archive created at %s\n' "$OUTPUT_PATH"
