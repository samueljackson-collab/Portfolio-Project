#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_DIR="$ROOT_DIR/infrastructure"
COMPOSE_FILE="$INFRA_DIR/docker-compose.yml"
ENV_FILE="$INFRA_DIR/.env"

if ! command -v docker &>/dev/null; then
  echo "[bootstrap] Docker is required but not found in PATH." >&2
  exit 1
fi

if ! command -v docker compose &>/dev/null; then
  echo "[bootstrap] Docker Compose plugin is required (Docker 20.10+)." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[bootstrap] Missing $ENV_FILE. Copy infrastructure/.env.example and customize secrets before bootstrapping." >&2
  exit 1
fi

echo "[bootstrap] Pulling latest container images and building custom services…"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull

echo "[bootstrap] Launching the AI analytics stack…"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build

echo "[bootstrap] Stack launched. Use scripts/validate_stack.sh to run post-launch checks."
