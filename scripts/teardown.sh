#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--env <environment>] [--dry-run]

Destroys Kubernetes workloads and Terraform-managed infrastructure.

Options:
  --env <environment>   Deployment environment to destroy. Default: dev.
  --dry-run             Print commands without executing them.
  -h, --help            Show this help.
USAGE
}

ENVIRONMENT="dev"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

echo "[teardown] environment=${ENVIRONMENT} dry-run=${DRY_RUN}"

run() {
  if [[ "${DRY_RUN}" == "true" ]]; then
    echo "[dry-run] $*"
  else
    echo "[exec] $*"
    eval "$@"
  fi
}

TF_DIR="$(cd "$(dirname "$0")/../infrastructure/terraform" && pwd)"
KUBE_DIR="$(cd "$(dirname "$0")/../infrastructure/kubernetes" && pwd)"

run "kubectl delete -k ${KUBE_DIR}/overlays/${ENVIRONMENT} --ignore-not-found"
run "terraform -chdir=${TF_DIR} destroy -var-file=env/${ENVIRONMENT}.tfvars -auto-approve"

printf '\nTeardown for %s complete.\n' "${ENVIRONMENT}"
