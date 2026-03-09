#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: db_migration_helper.sh [options]

Runs database migrations.

Options:
  --command CMD       Migration command
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

COMMAND=${COMMAND:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --command)
      COMMAND="$2"
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

if [[ -z ${COMMAND} ]]; then
  usage
  exit 1
fi

log info "Running migration command: ${COMMAND}"
if [[ ${DRY_RUN} == "true" ]]; then
  log info "dry-run: ${COMMAND}"
  exit 0
fi

bash -c "${COMMAND}"
