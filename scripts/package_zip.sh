#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUTPUT_DIR="$ROOT_DIR/reports"
ARCHIVE_NAME="portfolio-monorepo-$(date +%Y%m%d).tar.gz"

mkdir -p "$OUTPUT_DIR"

tar --exclude='node_modules' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.terraform' \
    --exclude='.git' \
    -czf "$OUTPUT_DIR/$ARCHIVE_NAME" -C "$ROOT_DIR" .

(cd "$OUTPUT_DIR" && sha256sum "$ARCHIVE_NAME" > "$ARCHIVE_NAME.sha256")

echo "Package created at $OUTPUT_DIR/$ARCHIVE_NAME"
