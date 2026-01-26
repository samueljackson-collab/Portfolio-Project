#!/usr/bin/env bash
set -euo pipefail

DB_NAME=${1:-${PGDATABASE:-}}

if [[ -z "${DB_NAME}" ]]; then
  echo "Usage: $0 <database>" >&2
  exit 1
fi

psql --set ON_ERROR_STOP=on --dbname "${DB_NAME}" -c "ANALYZE"
