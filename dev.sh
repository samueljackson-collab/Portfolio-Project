#!/usr/bin/env bash
set -euo pipefail

compose_cmd=${1:-up}

case "$compose_cmd" in
  up)
    docker-compose up --build
    ;;
  down)
    docker-compose down
    ;;
  logs)
    docker-compose logs -f
    ;;
  *)
    echo "Usage: ./dev.sh [up|down|logs]"
    exit 1
    ;;
esac
