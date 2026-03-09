#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: docker_cleanup.sh [options]

Cleans unused Docker containers, images, and volumes.

Options:
  --all             Remove all unused images
  --volumes         Remove unused volumes
  --dry-run         Show actions without executing
  --log-level LEVEL debug|info|warn|error
  -h, --help        Show this help
USAGE
}

ALL_IMAGES=false
REMOVE_VOLUMES=false

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      ALL_IMAGES=true
      shift
      ;;
    --volumes)
      REMOVE_VOLUMES=true
      shift
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

require_command docker

args=(system prune -f)
if [[ ${ALL_IMAGES} == true ]]; then
  args+=(--all)
fi
if [[ ${REMOVE_VOLUMES} == true ]]; then
  args+=(--volumes)
fi

log info "Running Docker cleanup"
run_cmd docker "${args[@]}"
