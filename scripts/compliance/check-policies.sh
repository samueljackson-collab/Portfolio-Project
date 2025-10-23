#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[COMPLIANCE] %s\n' "$*"
}

POLICY_FILE="security/compliance/policy-as-code.yaml"

if [ ! -f "$POLICY_FILE" ]; then
  log "Policy file $POLICY_FILE not found"
  exit 0
fi

log "Validating policy manifests"
if command -v kubeval >/dev/null 2>&1; then
  kubeval "$POLICY_FILE"
else
  log "kubeval not installed; performing schema check via kubectl --dry-run"
  kubectl apply --dry-run=client -f "$POLICY_FILE"
fi

log "Compliance checks completed"
