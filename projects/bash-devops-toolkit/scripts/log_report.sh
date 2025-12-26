#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: log_report.sh [options]

Generates a basic log severity report.

Options:
  --file PATH         Log file path
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

LOG_FILE=${LOG_FILE:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      LOG_FILE="$2"
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

if [[ -z ${LOG_FILE} ]]; then
  usage
  exit 1
fi

log info "Analyzing log file ${LOG_FILE}"

awk '
/ERROR/ {err++}
/WARN/ {warn++}
/INFO/ {info++}
END {printf "INFO:%d WARN:%d ERROR:%d\n", info, warn, err}' "${LOG_FILE}"
