#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: resource_usage.sh [options]

Reports CPU and memory usage.

Options:
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

parse_common_flags "$@"

cpu_usage=$(top -bn1 | awk '/Cpu/ {print 100 - $8}')
mem_usage=$(free -m | awk '/Mem/ {printf "%.2f", $3/$2*100}')

log info "CPU usage: ${cpu_usage}%"
log info "Memory usage: ${mem_usage}%"
