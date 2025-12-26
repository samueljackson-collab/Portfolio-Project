#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: filesystem_snapshot.sh [options]

Creates a filesystem snapshot using rsync.

Options:
  --source DIR        Source directory
  --destination DIR   Destination directory
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

SOURCE=${SOURCE:-""}
DESTINATION=${DESTINATION:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE="$2"
      shift 2
      ;;
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

if [[ -z ${SOURCE} || -z ${DESTINATION} ]]; then
  usage
  exit 1
fi

require_command rsync

snapshot_dir="${DESTINATION}/snapshot-$(date +%Y%m%d%H%M%S)"
log info "Creating snapshot ${snapshot_dir}"
run_cmd rsync -a --delete "${SOURCE}/" "${snapshot_dir}/"
