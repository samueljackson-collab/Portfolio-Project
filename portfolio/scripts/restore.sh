#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup-file> [container]" >&2
  exit 1
fi
BACKUP_FILE=$1
CONTAINER=${2:-portfolio-postgres}

echo "Restoring $BACKUP_FILE into container $CONTAINER"
cat "$BACKUP_FILE" | docker exec -i "$CONTAINER" psql -U postgres app
