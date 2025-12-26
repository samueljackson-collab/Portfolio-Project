#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

export PGPASSWORD

databases=$(psql -At -c "SELECT datname FROM pg_database WHERE datistemplate = false;")

for db in ${databases}; do
  echo "Vacuuming ${db}"
  psql -d "${db}" -c "VACUUM (ANALYZE);"
done
