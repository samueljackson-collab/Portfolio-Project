#!/usr/bin/env bash
# Deploy or update the production-grade AWS stack with Terraform.
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TF_DIR="${ROOT_DIR}/terraform"

if ! command -v terraform >/dev/null 2>&1; then
  echo "Terraform must be installed to deploy the infrastructure." >&2
  exit 1
fi

pushd "${TF_DIR}" >/dev/null
terraform init
terraform fmt -recursive
terraform validate
terraform plan "$@"
read -rp "Apply the plan? (y/N) " confirm
if [[ "${confirm}" =~ ^[Yy]$ ]]; then
  terraform apply "$@"
else
  echo "Skipping apply." >&2
fi
popd >/dev/null
