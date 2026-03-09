#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: blue_green_deploy.sh [options]

Swaps blue/green deployment directories via symlink.

Options:
  --blue DIR          Blue release directory
  --green DIR         Green release directory
  --current LINK      Current symlink path
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

BLUE_DIR=${BLUE_DIR:-""}
GREEN_DIR=${GREEN_DIR:-""}
CURRENT_LINK=${CURRENT_LINK:-"/var/www/current"}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --blue)
      BLUE_DIR="$2"
      shift 2
      ;;
    --green)
      GREEN_DIR="$2"
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

if [[ -z ${BLUE_DIR} || -z ${GREEN_DIR} ]]; then
  usage
  exit 1
fi

current_target=$(readlink -f "${CURRENT_LINK}" || true)
if [[ ${current_target} == "${BLUE_DIR}" ]]; then
  next_target=${GREEN_DIR}
else
  next_target=${BLUE_DIR}
fi

log info "Switching ${CURRENT_LINK} to ${next_target}"
run_cmd ln -sfn "${next_target}" "${CURRENT_LINK}"
