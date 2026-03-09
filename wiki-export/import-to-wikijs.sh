#!/bin/bash
# Auto-generated Wiki.js import helper
# Usage: WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=<token> ./import-to-wikijs.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

WIKIJS_URL="${WIKIJS_URL:-http://localhost:3000}"
WIKIJS_TOKEN="${WIKIJS_TOKEN:?Error: WIKIJS_TOKEN must be set}"

echo "Importing to Wiki.js at $WIKIJS_URL ..."

cd "$REPO_ROOT"

# Check for node
if ! command -v node &>/dev/null; then
  echo "Error: node is required"
  exit 1
fi

# Install deps if needed
if [ ! -d "wiki-js-scaffold/node_modules" ]; then
  echo "Installing wiki-js-scaffold dependencies..."
  cd wiki-js-scaffold && npm install && cd ..
fi

WIKIJS_URL="$WIKIJS_URL" WIKIJS_TOKEN="$WIKIJS_TOKEN" \
  node wiki-js-scaffold/scripts/import-to-wikijs.js

echo "Import complete!"
