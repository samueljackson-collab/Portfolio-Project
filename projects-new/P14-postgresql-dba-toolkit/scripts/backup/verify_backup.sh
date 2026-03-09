#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE=${1:-}

if [[ -z "${BACKUP_FILE}" ]]; then
  echo "Usage: $0 <backup-file>" >&2
  exit 1
fi

pg_restore --list "${BACKUP_FILE}" >/dev/null

echo "Backup verification passed: ${BACKUP_FILE}"
