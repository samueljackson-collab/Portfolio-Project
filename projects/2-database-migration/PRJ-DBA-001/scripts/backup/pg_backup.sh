#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"
: "${BACKUP_ROOT:=./backups}"
: "${BACKUP_FORMAT:=custom}"
: "${BACKUP_PREFIX:=pg_backup}"

export PGPASSWORD

timestamp=$(date +%Y-%m-%d_%H-%M-%S)
backup_dir="${BACKUP_ROOT}/${timestamp}"
mkdir -p "${backup_dir}"

case "${BACKUP_FORMAT}" in
  custom)
    output_file="${backup_dir}/${BACKUP_PREFIX}_${timestamp}.dump"
    pg_dump -Fc -f "${output_file}" "${PGDATABASE}"
    ;;
  directory)
    output_dir="${backup_dir}/${BACKUP_PREFIX}_${timestamp}.dir"
    pg_dump -Fd -j 4 -f "${output_dir}" "${PGDATABASE}"
    ;;
  plain)
    output_file="${backup_dir}/${BACKUP_PREFIX}_${timestamp}.sql"
    pg_dump -Fp -f "${output_file}" "${PGDATABASE}"
    ;;
  *)
    echo "Unsupported BACKUP_FORMAT: ${BACKUP_FORMAT}" >&2
    exit 1
    ;;
 esac

echo "Backup completed in ${backup_dir}"
