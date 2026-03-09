#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: log_rotate.sh [options]

Rotate and archive log files based on size.

Options:
  --log-dir DIR        Directory containing logs
  --archive-dir DIR    Directory for archived logs
  --max-size MB        Max size before rotation (default: 100)
  --dry-run            Show actions without executing
  --log-level LEVEL    debug|info|warn|error
  -h, --help           Show this help
USAGE
}

LOG_DIR=${LOG_DIR:-"/var/log"}
ARCHIVE_DIR=${ARCHIVE_DIR:-"/var/log/archive"}
MAX_SIZE_MB=${MAX_SIZE_MB:-100}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --log-dir)
      LOG_DIR="$2"
      shift 2
      ;;
    --archive-dir)
      ARCHIVE_DIR="$2"
      shift 2
      ;;
    --max-size)
      MAX_SIZE_MB="$2"
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

require_command gzip

run_cmd mkdir -p "${ARCHIVE_DIR}"

find "${LOG_DIR}" -type f -name "*.log" | while read -r logfile; do
  size_mb=$(du -m "${logfile}" | awk '{print $1}')
  if (( size_mb >= MAX_SIZE_MB )); then
    timestamp=$(date +%Y%m%d%H%M%S)
    archive_file="${ARCHIVE_DIR}/$(basename "${logfile}").${timestamp}.gz"
    log info "Rotating ${logfile} -> ${archive_file}"
    run_cmd cp "${logfile}" "${archive_file%.gz}"
    run_cmd gzip "${archive_file%.gz}"
    run_cmd truncate -s 0 "${logfile}"
  fi
 done
