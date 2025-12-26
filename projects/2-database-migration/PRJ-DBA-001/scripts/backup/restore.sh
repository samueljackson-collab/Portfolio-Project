#!/usr/bin/env bash
set -euo pipefail

backup_path="${1:-}"
target_db="${2:-}"

if [[ -z "${backup_path}" || -z "${target_db}" ]]; then
  echo "Usage: $0 <backup_path> <target_db>" >&2
  exit 1
fi

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

export PGPASSWORD

case "${backup_path}" in
  *.dump)
    pg_restore --clean --if-exists --dbname "${target_db}" "${backup_path}"
    ;;
  *.sql)
    psql --dbname "${target_db}" -f "${backup_path}"
    ;;
  *.dir)
    pg_restore --clean --if-exists --dbname "${target_db}" "${backup_path}"
    ;;
  *)
    echo "Unsupported backup format: ${backup_path}" >&2
    exit 1
    ;;
 esac

echo "Restore complete for ${target_db}"
