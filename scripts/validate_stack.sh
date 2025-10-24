#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_DIR="$ROOT_DIR/infrastructure"
COMPOSE_FILE="$INFRA_DIR/docker-compose.yml"
ENV_FILE="$INFRA_DIR/.env"

if ! command -v docker &>/dev/null; then
  echo "[validate] Docker is required but not found in PATH." >&2
  exit 1
fi

if ! command -v curl &>/dev/null; then
  echo "[validate] curl is required for health checks." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[validate] Missing $ENV_FILE. Copy infrastructure/.env.example and customize secrets before validating." >&2
  exit 1
fi

source "$ENV_FILE"

echo "[validate] Container state summary:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

check_failed=0

function check_http() {
  local label="$1"
  local url="$2"
  echo "[validate] Checking $label at $url"
  if curl -fsS "$url" >/dev/null; then
    echo "[validate] ✔ $label healthy"
  else
    echo "[validate] ✖ $label failed health check" >&2
    check_failed=1
  fi
}

check_http "Matomo" "http://localhost:${MATOMO_HTTP_PORT:-8080}/"
check_http "n8n" "http://localhost:${N8N_HTTP_PORT:-5678}/rest/healthz"
check_http "LLM" "http://localhost:${LLM_HTTP_PORT:-8081}/health"
check_http "Stable Diffusion" "http://localhost:${STABLE_DIFFUSION_HTTP_PORT:-9090}/health"
check_http "Whisper" "http://localhost:${WHISPER_HTTP_PORT:-9000}/health"
check_http "Scrapyd" "http://localhost:${SCRAPYD_HTTP_PORT:-6800}/"

if [[ "$check_failed" -eq 0 ]]; then
  echo "[validate] All services responded successfully."
else
  echo "[validate] One or more services failed health checks. Inspect logs with make logs." >&2
  exit 1
fi
