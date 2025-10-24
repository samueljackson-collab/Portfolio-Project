#!/usr/bin/env bash
set -euo pipefail

echo "\n>>> Bootstrapping development environment"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required to run the dev environment" >&2
  exit 1
fi

docker compose up --build
