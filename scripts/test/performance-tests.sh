#!/usr/bin/env bash
set -euo pipefail

API_URL=${1:-"http://localhost:8080"}
DURATION=${2:-5}

log() {
  printf '[PERF] %s\n' "$*"
}

if ! command -v hey >/dev/null 2>&1; then
  log "hey load generator not installed; skipping performance test"
  exit 0
fi

log "Running performance probe against $API_URL for $DURATION seconds"
hey -z "${DURATION}s" -q 10 "$API_URL/health" >/dev/null
log "Performance probe completed"
