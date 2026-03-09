#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: retention_policy.sh [options]

Applies retention policy to backup directory.

Options:
  --directory DIR     Directory containing backups
  --days DAYS         Retention days (default: 30)
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

BACKUP_DIR=${BACKUP_DIR:-"/var/backups"}
RETENTION_DAYS=${RETENTION_DAYS:-30}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --directory)
      BACKUP_DIR="$2"
      shift 2
      ;;
    --days)
      RETENTION_DAYS="$2"
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

log info "Applying retention policy: ${RETENTION_DAYS} days"

find "${BACKUP_DIR}" -type f -mtime "+${RETENTION_DAYS}" | while read -r file; do
  log info "Removing ${file}"
  run_cmd rm -f "${file}"
 done
