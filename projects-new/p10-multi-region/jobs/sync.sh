#!/usr/bin/env bash
set -euo pipefail
mode=${1:-copy}
if [[ "$mode" == "--verify" ]]; then
  echo "Verifying snapshot checksum"
else
  echo "Copying snapshot from primary to secondary"
fi
