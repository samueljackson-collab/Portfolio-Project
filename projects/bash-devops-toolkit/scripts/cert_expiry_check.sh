#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: cert_expiry_check.sh [options] host:port [...]

Checks TLS certificate expiration dates.

Options:
  --warning-days DAYS  Warn if expires within days (default: 30)
  --dry-run            Show actions without executing
  --log-level LEVEL    debug|info|warn|error
  -h, --help           Show this help
USAGE
}

WARNING_DAYS=${WARNING_DAYS:-30}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --warning-days)
      WARNING_DAYS="$2"
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

require_command openssl

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

for target in "$@"; do
  host=${target%:*}
  port=${target#*:}
  expiry=$(echo | openssl s_client -servername "${host}" -connect "${host}:${port}" 2>/dev/null \
    | openssl x509 -noout -enddate | cut -d= -f2)
  expiry_ts=$(date -d "${expiry}" +%s)
  now_ts=$(date +%s)
  days_left=$(( (expiry_ts - now_ts) / 86400 ))
  if (( days_left <= WARNING_DAYS )); then
    log warn "${host}:${port} certificate expires in ${days_left} days (${expiry})"
  else
    log info "${host}:${port} certificate expires in ${days_left} days (${expiry})"
  fi
 done
