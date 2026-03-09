#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: disk_monitor.sh [options]

Checks disk usage and warns when above threshold.

Options:
  --threshold PERCENT  Threshold percentage (default: 80)
  --dry-run            Show actions without executing
  --log-level LEVEL    debug|info|warn|error
  -h, --help           Show this help
USAGE
}

THRESHOLD=${THRESHOLD:-80}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --threshold)
      THRESHOLD="$2"
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

log info "Checking disk usage"

while read -r line; do
  usage=$(echo "${line}" | awk '{print $5}' | tr -d '%')
  mount=$(echo "${line}" | awk '{print $6}')
  if (( usage >= THRESHOLD )); then
    log warn "Disk usage at ${usage}% on ${mount}"
  else
    log info "Disk usage at ${usage}% on ${mount}"
  fi
 done < <(df -P | tail -n +2)
