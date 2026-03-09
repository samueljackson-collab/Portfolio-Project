#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: rolling_update.sh [options]

Triggers a Kubernetes rolling update.

Options:
  --deployment NAME   Deployment name
  --namespace NS      Namespace (default: default)
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

DEPLOYMENT=${DEPLOYMENT:-""}
NAMESPACE=${NAMESPACE:-"default"}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --deployment)
      DEPLOYMENT="$2"
      shift 2
      ;;
    --namespace)
      NAMESPACE="$2"
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

if [[ -z ${DEPLOYMENT} ]]; then
  usage
  exit 1
fi

require_command kubectl

log info "Rolling update for deployment ${DEPLOYMENT} in ${NAMESPACE}"
run_cmd kubectl rollout restart "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"
run_cmd kubectl rollout status "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"
