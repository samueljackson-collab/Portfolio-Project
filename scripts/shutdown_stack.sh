#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_DIR="$ROOT_DIR/infrastructure"
COMPOSE_FILE="$INFRA_DIR/docker-compose.yml"
ENV_FILE="$INFRA_DIR/.env"

if ! command -v docker &>/dev/null; then
  echo "[shutdown] Docker is required but not found in PATH." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[shutdown] Missing $ENV_FILE. Copy infrastructure/.env.example to .env before managing the stack." >&2
  exit 1
fi

echo "[shutdown] Stopping and removing containers…"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down "$@"
