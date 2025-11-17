#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

check_endpoint() {
  local name=$1
  local url=$2
  if curl -sf "$url" >/dev/null; then
    echo "[PASS] ${name} reachable"
  else
    echo "[FAIL] ${name} unreachable"
    return 1
  fi
}

echo "== Endpoint checks =="
check_endpoint "Prometheus" "http://localhost:9090/-/healthy"
check_endpoint "Grafana" "http://localhost:3000/api/health"
check_endpoint "Alertmanager" "http://localhost:9093/-/healthy"
check_endpoint "Loki" "http://localhost:3100/ready"


echo "== Data checks =="
if curl -sf "http://localhost:9090/api/v1/query?query=up" | grep -q '"up"'; then
  echo "[PASS] Prometheus returning metrics"
else
  echo "[FAIL] Prometheus query failed"
fi

# Fire test alert and confirm Alertmanager ingestion
cat <<'ALERT' | curl -sf -XPOST -H 'Content-Type: application/json' --data-binary @- http://localhost:9093/api/v1/alerts >/dev/null && echo "[PASS] Test alert sent"
[
  {
    "labels": {"alertname": "TestAlert", "severity": "warning"},
    "annotations": {"summary": "Manual test"}
  }
]
ALERT

# Loki ingestion smoke test
logger "promtail-test-line"
sleep 2
if curl -sf "http://localhost:3100/loki/api/v1/query?query={job=\"docker\"}" | grep -q "promtail-test-line"; then
  echo "[PASS] Loki received test log"
else
  echo "[WARN] Could not verify Loki ingestion"
fi

# Summarize container states
 docker compose -f "$COMPOSE_FILE" ps
