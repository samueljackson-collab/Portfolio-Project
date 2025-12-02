#!/usr/bin/env bash
set -euo pipefail
action=${1:-down}
if [[ "$action" == "down" ]]; then
  echo "Simulating primary failure"
else
  echo "Restoring primary health"
fi
