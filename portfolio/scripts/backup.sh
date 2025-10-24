#!/usr/bin/env bash
set -euo pipefail
BACKUP_DIR="$(cd "$(dirname "$0")/.." && pwd)/data/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP="$(date +%F-%H%M%S)"
CONTAINER=${1:-portfolio-postgres}
FILE="$BACKUP_DIR/postgres-$TIMESTAMP.sql"

echo "Creating PostgreSQL backup at $FILE"
docker exec "$CONTAINER" pg_dump -U postgres app > "$FILE"
shasum -a 256 "$FILE"
