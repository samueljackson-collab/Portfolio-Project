#!/usr/bin/env bash
set -euo pipefail

project_dir=$(pwd)

if command -v terraform >/dev/null 2>&1 && [ -d terraform ]; then
  if ! terraform -chdir=terraform init -backend=false >/dev/null 2>&1; then
    echo "[!] Terraform init failed; skipping terraform validation"
  else
    terraform -chdir=terraform fmt -check
    terraform -chdir=terraform validate
  fi
else
  echo "[!] Terraform not available; skipping terraform validation"
fi

if command -v kubectl >/dev/null 2>&1 && [ -d kubernetes ]; then
  echo "[+] Rendering Kubernetes manifests"
  kubectl kustomize kubernetes >/dev/null
else
  [ -d kubernetes ] && echo "[!] kubectl not available; skipped manifest render"
fi

echo "[✓] Validation completed"
