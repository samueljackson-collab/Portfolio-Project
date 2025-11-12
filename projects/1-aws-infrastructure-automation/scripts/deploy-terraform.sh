#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT=${1:-dev}
TF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../terraform && pwd)"

log() {
  printf '🛠️  %s\n' "$1"
}

ensure_prereqs() {
  command -v terraform >/dev/null 2>&1 || {
    echo "Terraform is required but not found in PATH." >&2
    exit 1
  }
  if [[ ! -f "${TF_DIR}/${ENVIRONMENT}.tfvars" ]]; then
    echo "No tfvars file found for environment '${ENVIRONMENT}'." >&2
    exit 1
  fi
}

run_plan_apply() {
  cd "${TF_DIR}"

  log "Initialising backend and providers"
  terraform init -backend-config=backend.hcl -reconfigure

  log "Validating configuration"
  terraform validate

  log "Planning changes for ${ENVIRONMENT}"
  terraform plan -var-file="${ENVIRONMENT}.tfvars" -out=.tfplan

  log "Applying plan"
  terraform apply -auto-approve .tfplan

  log "Infrastructure deployed"
}

ensure_prereqs
run_plan_apply
