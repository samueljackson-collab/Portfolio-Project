#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: config_deploy.sh [options]

Deploys configuration files and restarts a service.

Options:
  --source DIR        Source config directory
  --destination DIR   Destination directory
  --service NAME      Systemd service name
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

SOURCE=${SOURCE:-""}
DESTINATION=${DESTINATION:-""}
SERVICE_NAME=${SERVICE_NAME:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --destination)
      DESTINATION="$2"
      shift 2
      ;;
    --service)
      SERVICE_NAME="$2"
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

if [[ -z ${SOURCE} || -z ${DESTINATION} || -z ${SERVICE_NAME} ]]; then
  usage
  exit 1
fi

require_command rsync
require_command systemctl

log info "Deploying config from ${SOURCE} to ${DESTINATION}"
run_cmd rsync -av "${SOURCE}/" "${DESTINATION}/"
log info "Restarting service ${SERVICE_NAME}"
run_cmd systemctl restart "${SERVICE_NAME}"
