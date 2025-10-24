#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

printf '🔍 Validating project directory layout...\n'
for required in terraform cdk pulumi scripts; do
  if [[ ! -d "${PROJECT_ROOT}/${required}" ]]; then
    echo "Missing required directory: ${required}" >&2
    exit 1
  fi
  printf '  • %s present\n' "${required}"
fi

printf '\n📄 Checking Terraform variables files...\n'
for env_file in dev.tfvars production.tfvars; do
  if [[ ! -f "${PROJECT_ROOT}/terraform/${env_file}" ]]; then
    echo "Terraform variables file ${env_file} missing." >&2
    exit 1
  fi
  printf '  • %s ready\n' "${env_file}"
fi

printf '\n✅ Project structure looks good. Use the deploy scripts in ./scripts/ to provision your preferred stack.\n'
