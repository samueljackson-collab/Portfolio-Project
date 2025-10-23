#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${1:-"http://localhost:3000"}
API_URL=${2:-"http://localhost:8080"}

log() {
  printf '[SMOKE] %s\n' "$*"
}

curl_check() {
  local url="$1"
  if curl --fail --silent --show-error "$url" >/dev/null; then
    log "OK - ${url}"
  else
    log "FAIL - ${url}"
    return 1
  fi
}

log "Starting smoke tests"

curl_check "$BASE_URL"
curl_check "$API_URL/health"
curl_check "$API_URL/health/db"
curl_check "$API_URL/health/redis"

log "Smoke tests completed"
