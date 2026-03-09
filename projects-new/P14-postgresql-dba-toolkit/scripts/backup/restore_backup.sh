#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE=${1:-}
TARGET_DB=${2:-}

if [[ -z "${BACKUP_FILE}" || -z "${TARGET_DB}" ]]; then
  echo "Usage: $0 <backup-file> <target-db>" >&2
  exit 1
fi

pg_restore --clean --if-exists --dbname "${TARGET_DB}" "${BACKUP_FILE}"

echo "Restore completed for ${TARGET_DB}"
