#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: rollback.sh [options]

Rolls back to a previous release by switching a symlink.

Options:
  --previous DIR      Previous release directory
  --current LINK      Current symlink path
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

PREVIOUS_DIR=${PREVIOUS_DIR:-""}
CURRENT_LINK=${CURRENT_LINK:-"/var/www/current"}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --previous)
      PREVIOUS_DIR="$2"
      shift 2
      ;;
    --current)
      CURRENT_LINK="$2"
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

if [[ -z ${PREVIOUS_DIR} ]]; then
  usage
  exit 1
fi

log info "Rolling back ${CURRENT_LINK} to ${PREVIOUS_DIR}"
run_cmd ln -sfn "${PREVIOUS_DIR}" "${CURRENT_LINK}"
