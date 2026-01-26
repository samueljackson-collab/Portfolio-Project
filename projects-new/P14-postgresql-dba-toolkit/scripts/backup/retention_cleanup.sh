#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)

if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${PROJECT_ROOT}/.env"
  set +a
fi

BACKUP_DIR=${BACKUP_DIR:-${PROJECT_ROOT}/backups}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-14}

find "${BACKUP_DIR}" -type f -name "*.dump" -mtime "+${BACKUP_RETENTION_DAYS}" -print -delete
