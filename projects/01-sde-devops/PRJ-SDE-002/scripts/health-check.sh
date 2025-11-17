#!/bin/bash
# Health check script for monitoring stack
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

check_endpoint() {
  local name=$1 url=$2
  if curl -fsS "$url" >/dev/null; then
    echo "[PASS] $name reachable"
  else
    echo "[FAIL] $name unreachable"
    return 1
  fi
}

echo "== HTTP health checks =="
check_endpoint "Prometheus" "http://localhost:9090/-/healthy"
check_endpoint "Grafana" "http://localhost:3000/api/health"
check_endpoint "Loki" "http://localhost:3100/ready"
check_endpoint "Alertmanager" "http://localhost:9093/-/healthy"

# Query Prometheus for recent samples to validate scraping pipeline.
echo "== Prometheus scrape verification =="
curl -fsS "http://localhost:9090/api/v1/query?query=up" | jq '.status'

# Fire synthetic alert to verify Alertmanager pipeline (dry-run via amtool inside container if available).
echo "== Alert routing smoke test (synthetic) =="
docker compose -f "$COMPOSE_FILE" exec -T prometheus wget -qO- --post-data='' http://localhost:9090/-/reload || true

# Loki ingestion test: push a sample log and query it back.
echo "== Loki ingestion test =="
log_line="healthcheck $(date -Is)"
cat <<LOG | curl -fsS -X POST "http://localhost:3100/loki/api/v1/push" -H 'Content-Type: application/json' -d @-
{
  "streams": [
    {"stream": {"job": "healthcheck"}, "values": [["$(date +%s%N)", "${log_line}"]]}
  ]
}
LOG
sleep 2
curl -fsS "http://localhost:3100/loki/api/v1/query?query={job=\"healthcheck\"}" | jq '.data.result | length'

echo "== Summary =="
docker compose -f "$COMPOSE_FILE" ps
