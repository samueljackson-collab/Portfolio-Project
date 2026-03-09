#!/bin/bash
# Run this to import all pages into Wiki.js
# Set WIKIJS_URL and WIKIJS_TOKEN environment variables first

set -e
WIKIJS_URL="${WIKIJS_URL:-http://localhost:3000}"
WIKIJS_TOKEN="${WIKIJS_TOKEN:?WIKIJS_TOKEN must be set}"

cd "$(dirname "$0")/.."
WIKIJS_URL="$WIKIJS_URL" WIKIJS_TOKEN="$WIKIJS_TOKEN" \
  node wiki-js-scaffold/scripts/import-to-wikijs.js
