#!/usr/bin/env bash
set -euo pipefail

TARGET_DB=${1:-}
TARGET_USER=${2:-}

if [[ -z "${TARGET_DB}" || -z "${TARGET_USER}" ]]; then
  echo "Usage: $0 <database> <username>" >&2
  exit 1
fi

psql --set ON_ERROR_STOP=on --dbname "${TARGET_DB}" <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${TARGET_DB}'
  AND usename = '${TARGET_USER}'
  AND pid <> pg_backend_pid();
SQL
