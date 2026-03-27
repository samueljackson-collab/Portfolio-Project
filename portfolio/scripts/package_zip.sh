#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT="portfolio-dist.zip"

echo "Packaging repository into $OUTPUT"
cd "$ROOT_DIR"
zip -r "$OUTPUT" . \
  -x "*/node_modules/*" "*/.terraform/*" "*/__pycache__/*" "*.zip"
