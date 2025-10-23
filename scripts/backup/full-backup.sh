#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR=${1:-backup/manual-$(date -u +%Y%m%d-%H%M%S)}
mkdir -p "$TARGET_DIR"

log() {
  printf '[BACKUP] %s\n' "$*"
}

log "Capturing cluster resources"
if command -v kubectl >/dev/null 2>&1; then
  kubectl get all -A -o yaml > "$TARGET_DIR/k8s-resources.yaml"
fi

log "Archiving Terraform state references"
if [ -f infrastructure/terraform/terraform.tfstate ]; then
  cp infrastructure/terraform/terraform.tfstate "$TARGET_DIR/"
fi

log "Backup stored in $TARGET_DIR"
