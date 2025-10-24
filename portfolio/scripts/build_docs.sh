#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT="$ROOT_DIR/docs/_site"
mkdir -p "$OUTPUT"
if ! command -v pandoc >/dev/null; then
  echo "pandoc is required to build docs. Install pandoc and retry." >&2
  exit 0
fi
pandoc "$ROOT_DIR/README.md" -o "$OUTPUT/portfolio.html"
