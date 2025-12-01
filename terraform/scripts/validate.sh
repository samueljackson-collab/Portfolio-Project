#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${TERRAFORM_DIR}/.." && pwd)"

print_step() {
  echo "==> $1"
}

print_step "Terraform init/validate"
terraform -chdir="$TERRAFORM_DIR" init -backend=false -input=false
terraform -chdir="$TERRAFORM_DIR" validate

tfsec_path=$(command -v tfsec || true)
if [[ -n "$tfsec_path" ]]; then
  print_step "tfsec scan"
  tfsec "$TERRAFORM_DIR" --no-color --minimum-severity LOW
else
  echo "[warn] tfsec not installed; skipping security scan"
fi

checkov_path=$(command -v checkov || true)
if [[ -n "$checkov_path" ]]; then
  print_step "Checkov scan"
  checkov -d "$TERRAFORM_DIR" --quiet --framework terraform
else
  echo "[warn] Checkov not installed; skipping policy scan"
fi

pytest_path=$(command -v pytest || true)
if [[ -n "$pytest_path" ]]; then
  print_step "pytest validation suite"
  python -m pytest "$REPO_ROOT/tests/validation" -q
else
  echo "[warn] pytest not installed; skipping tests in tests/validation"
fi

print_step "Validation complete"
