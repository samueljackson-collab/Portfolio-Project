#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--env <environment>] [--dry-run]

Deploys Terraform infrastructure and applies Kubernetes manifests.

Options:
  --env <environment>   Deployment environment (dev|staging|prod). Default: dev.
  --dry-run             Print commands without executing them.
  -h, --help            Show this message.
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

echo "[deploy] environment=${ENVIRONMENT} dry-run=${DRY_RUN}"

run() {
  if [[ "${DRY_RUN}" == "true" ]]; then
    echo "[dry-run] $*"
  else
    echo "[exec] $*"
    eval "$@"
  fi
}

export TF_IN_AUTOMATION=1
export PORTFOLIO_ENV="${ENVIRONMENT}"

TF_DIR="$(cd "$(dirname "$0")/../infrastructure/terraform" && pwd)"
KUBE_DIR="$(cd "$(dirname "$0")/../infrastructure/kubernetes" && pwd)"

run "terraform -chdir=${TF_DIR} init"
run "terraform -chdir=${TF_DIR} apply -var-file=env/${ENVIRONMENT}.tfvars -auto-approve"
run "aws eks update-kubeconfig --name portfolio-${ENVIRONMENT} --region us-west-2"
run "kubectl apply -k ${KUBE_DIR}/overlays/${ENVIRONMENT}"

printf '\nDeployment for %s complete.\n' "${ENVIRONMENT}"
