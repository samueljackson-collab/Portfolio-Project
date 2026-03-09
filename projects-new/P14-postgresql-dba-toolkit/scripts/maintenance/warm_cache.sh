#!/usr/bin/env bash
set -euo pipefail

DB_NAME=${1:-${PGDATABASE:-}}
TABLE_NAME=${2:-}

if [[ -z "${DB_NAME}" || -z "${TABLE_NAME}" ]]; then
  echo "Usage: $0 <database> <table>" >&2
  exit 1
fi

psql --set ON_ERROR_STOP=on --dbname "${DB_NAME}" -c "SELECT count(*) FROM \"${TABLE_NAME}\";"
