#!/usr/bin/env bash
set -euo pipefail

ROLLBACK_FILE=${1:-}

if [[ -z "${ROLLBACK_FILE}" ]]; then
  echo "Usage: $0 <rollback-sql-file>" >&2
  exit 1
fi

FILENAME=$(basename "${ROLLBACK_FILE}")

psql --set ON_ERROR_STOP=on --file "${ROLLBACK_FILE}"
psql --set ON_ERROR_STOP=on -c "DELETE FROM schema_migrations WHERE filename='${FILENAME}'"

echo "Rollback applied for ${FILENAME}"
