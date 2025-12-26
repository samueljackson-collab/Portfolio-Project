#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: service_health.sh [options] service1 service2 ...

Checks systemd service health.

Options:
  --dry-run            Show actions without executing
  --log-level LEVEL    debug|info|warn|error
  -h, --help           Show this help
USAGE
}

parse_common_flags "$@"

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

require_command systemctl

for service in "$@"; do
  if systemctl is-active --quiet "${service}"; then
    log info "${service} is active"
  else
    log warn "${service} is not active"
  fi
 done
