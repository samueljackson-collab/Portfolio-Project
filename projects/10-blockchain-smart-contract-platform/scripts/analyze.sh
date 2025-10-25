#!/bin/bash
set -euo pipefail

if ! command -v slither >/dev/null; then
  echo "Install slither: pip install slither-analyzer" >&2
  exit 1
fi

slither ./contracts
