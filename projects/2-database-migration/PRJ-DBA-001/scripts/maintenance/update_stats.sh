#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

export PGPASSWORD

DATABASE="${1:-}"
if [[ -z "${DATABASE}" ]]; then
  DATABASES=$(psql -At -c "SELECT datname FROM pg_database WHERE datistemplate = false;")
else
  DATABASES=${DATABASE}
fi

for db in ${DATABASES}; do
  echo "Analyzing ${db}"
  psql -d "${db}" -c "ANALYZE;"
done
