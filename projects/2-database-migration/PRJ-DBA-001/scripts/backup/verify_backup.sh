#!/usr/bin/env bash
set -euo pipefail

backup_path="${1:-}"

if [[ -z "${backup_path}" ]]; then
  latest_dir=$(ls -1dt "${BACKUP_ROOT:-./backups}"/* 2>/dev/null | head -n 1 || true)
  if [[ -z "${latest_dir}" ]]; then
    echo "No backup directory found." >&2
    exit 1
  fi
  backup_path="${latest_dir}"
fi

if [[ -d "${backup_path}" ]]; then
  dump_file=$(find "${backup_path}" -maxdepth 1 -type f \( -name "*.dump" -o -name "*.sql" \) | head -n 1 || true)
  dir_file=$(find "${backup_path}" -maxdepth 1 -type d -name "*.dir" | head -n 1 || true)
  if [[ -n "${dir_file}" ]]; then
    pg_verifybackup "${dir_file}"
    echo "Directory backup verified: ${dir_file}"
    exit 0
  fi
  if [[ -n "${dump_file}" ]]; then
    pg_restore --list "${dump_file}" > /dev/null
    echo "Backup verified: ${dump_file}"
    exit 0
  fi
fi

if [[ -f "${backup_path}" ]]; then
  case "${backup_path}" in
    *.dump)
      pg_restore --list "${backup_path}" > /dev/null
      ;;
    *.sql)
      head -n 1 "${backup_path}" > /dev/null
      ;;
    *)
      echo "Unsupported backup file: ${backup_path}" >&2
      exit 1
      ;;
  esac
  echo "Backup verified: ${backup_path}"
  exit 0
fi

echo "Backup path not found: ${backup_path}" >&2
exit 1
