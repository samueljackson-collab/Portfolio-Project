#!/usr/bin/env bash
set -euo pipefail

project_dir=$(pwd)

if command -v terraform >/dev/null 2>&1 && [ -d terraform ]; then
  echo "[+] Running terraform init/apply for $(basename "$project_dir")"
  terraform -chdir=terraform init -upgrade
  terraform -chdir=terraform apply -auto-approve
else
  echo "[!] Terraform not available; skipping terraform apply"
fi

if command -v kubectl >/dev/null 2>&1 && [ -d kubernetes ]; then
  echo "[+] Applying Kubernetes manifests"
  kubectl apply -k kubernetes
else
  [ -d kubernetes ] && echo "[!] kubectl not available; skipped Kubernetes apply"
fi

if command -v docker >/dev/null 2>&1 && [ -f docker-compose.yml ]; then
  echo "[+] Launching docker compose stack"
  docker compose up -d
elif [ -f docker-compose.yml ]; then
  echo "[!] docker not available; skipped docker compose"
fi

echo "[+] Deployment complete"
