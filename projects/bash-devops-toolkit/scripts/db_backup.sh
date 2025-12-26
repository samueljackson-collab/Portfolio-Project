#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: db_backup.sh [options]

Creates a PostgreSQL database backup.

Options:
  --database NAME      Database name (env: DB_NAME)
  --user USER          Database user (env: DB_USER)
  --host HOST          Database host (env: DB_HOST)
  --port PORT          Database port (env: DB_PORT)
  --output DIR         Output directory (env: BACKUP_DIR)
  --dry-run            Show actions without executing
  --log-level LEVEL    debug|info|warn|error
  -h, --help           Show this help
USAGE
}

DB_NAME=${DB_NAME:-""}
DB_USER=${DB_USER:-""}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-5432}
BACKUP_DIR=${BACKUP_DIR:-"/var/backups"}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --database)
      DB_NAME="$2"
      shift 2
      ;;
    --user)
      DB_USER="$2"
      shift 2
      ;;
    --host)
      DB_HOST="$2"
      shift 2
      ;;
    --port)
      DB_PORT="$2"
      shift 2
      ;;
    --output)
      BACKUP_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
 done

if [[ -z ${DB_NAME} || -z ${DB_USER} ]]; then
  usage
  exit 1
fi

require_command pg_dump

run_cmd mkdir -p "${BACKUP_DIR}"

stamp=$(date +%Y%m%d%H%M%S)
backup_file="${BACKUP_DIR}/${DB_NAME}_${stamp}.sql.gz"

log info "Creating backup ${backup_file}"
run_cmd pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}" | gzip > "${backup_file}"
