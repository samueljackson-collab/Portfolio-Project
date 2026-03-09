#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

export PGPASSWORD

usage() {
  echo "Usage: $0 --database <db> [--table <schema.table>]" >&2
}

DATABASE=""
TABLE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --database)
      DATABASE="$2"
      shift 2
      ;;
    --table)
      TABLE="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
 done

if [[ -z "${DATABASE}" ]]; then
  usage
  exit 1
fi

if [[ -n "${TABLE}" ]]; then
  psql -d "${DATABASE}" -c "REINDEX TABLE ${TABLE};"
else
  psql -d "${DATABASE}" -c "REINDEX DATABASE ${DATABASE};"
fi
