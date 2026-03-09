#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: restore_backup.sh [options] archive

Restores a tar.gz backup archive.

Options:
  --destination DIR   Destination directory
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

DESTINATION=${DESTINATION:-"/"}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --destination)
      DESTINATION="$2"
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

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

archive="$1"
require_command tar

log info "Restoring ${archive} to ${DESTINATION}"
run_cmd tar -xzf "${archive}" -C "${DESTINATION}"
