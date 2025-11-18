#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

check_endpoint() {
  local name=$1
  local url=$2
  echo "Checking ${name} at ${url}" && curl -sf "${url}" >/dev/null
}

check_prometheus_query() {
  local query=$1
  curl -sf "http://localhost:9090/api/v1/query?query=${query}" | jq -e '.status == "success"' >/dev/null
}

check_loki() {
  curl -sf -G --data-urlencode "query={job='varlogs'}" "http://localhost:3100/loki/api/v1/query" >/dev/null
}

send_test_alert() {
  echo "Firing test alert via amtool"
  docker run --rm --network host -v "${PROJECT_ROOT}/alertmanager:/etc/alertmanager" prom/alertmanager:v0.26.0 \
    amtool --alertmanager.url=http://localhost:9093 alert add TestAlert instance=test severity=warning --startsAt=$(date --iso-8601=seconds)
}

check_endpoint "Prometheus" "http://localhost:9090/-/healthy"
check_endpoint "Grafana" "http://localhost:3000/api/health"
check_endpoint "Loki" "http://localhost:3100/ready"
check_endpoint "Alertmanager" "http://localhost:9093/-/ready"

check_prometheus_query "up"
check_loki
send_test_alert

echo "Health check completed"
