#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="artifacts"
mkdir -p "$OUTPUT_DIR"

ARCHIVE_NAME="portfolio-monorepo-$(date +%Y%m%d%H%M%S).zip"

zip -r "$OUTPUT_DIR/$ARCHIVE_NAME" \
  backend frontend e2e-tests infra monitoring docs \
  README.md CHANGELOG.md LICENSE \
  -x "**/node_modules/*" "**/__pycache__/*" "**/.terraform/*"

echo "Created $OUTPUT_DIR/$ARCHIVE_NAME"
