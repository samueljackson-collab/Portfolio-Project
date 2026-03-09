#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: alert_handler.sh [options]

Sends alert notifications to a webhook.

Options:
  --webhook URL       Webhook URL
  --message TEXT      Alert message
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

WEBHOOK_URL=${WEBHOOK_URL:-""}
MESSAGE=${MESSAGE:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --webhook)
      WEBHOOK_URL="$2"
      shift 2
      ;;
    --message)
      MESSAGE="$2"
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

if [[ -z ${WEBHOOK_URL} || -z ${MESSAGE} ]]; then
  usage
  exit 1
fi

require_command curl

payload=$(printf '{"text": "%s"}' "${MESSAGE}")
log info "Sending alert"
run_cmd curl -sS -X POST -H "Content-Type: application/json" -d "${payload}" "${WEBHOOK_URL}"
