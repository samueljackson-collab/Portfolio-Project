#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { printf "%b[HEALTH]%b %s\n" "$GREEN" "$NC" "$1"; }
warn() { printf "%b[WARN]%b %s\n" "$YELLOW" "$NC" "$1"; }
fail() { printf "%b[ERROR]%b %s\n" "$RED" "$NC" "$1"; exit 1; }

check_endpoint() {
  local name=$1; local url=$2
  if curl -fsS "$url" >/dev/null; then
    log "$name healthy"
  else
    fail "$name unreachable at $url"
  fi
}

log "Checking HTTP health endpoints"
check_endpoint "Prometheus" "http://localhost:9090/-/healthy"
check_endpoint "Grafana" "http://localhost:3000/api/health"
check_endpoint "Alertmanager" "http://localhost:9093/-/healthy"
check_endpoint "Loki" "http://localhost:3100/ready"

log "Verifying Prometheus recent samples"
if curl -fsS "http://localhost:9090/api/v1/query?query=up" | grep -q '"value"'; then
  log "Prometheus returning metrics"
else
  fail "Prometheus query failed"
fi

log "Testing alert pipeline with synthetic alert"
if command -v amtool >/dev/null 2>&1; then
  amtool alert add SyntheticAlert severity=warning instance=health-check expires=$(date -d "+5 minutes" +%s) || warn "amtool test failed"
else
  warn "amtool not installed; skip synthetic alert"
fi

log "Validating Loki ingestion"
logger "promtail-health-check $(date)" || warn "logger command unavailable"
if curl -fsS "http://localhost:3100/loki/api/v1/query?query=count_over_time(%7Bjob%3D%27varlogs%27%7D%5B5m%5D)" | grep -q 'data'; then
  log "Loki responding to queries"
else
  warn "Loki query failed"
fi

log "Health check completed"
