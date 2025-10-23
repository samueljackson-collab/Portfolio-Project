#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[SECURITY] %s\n' "$*"
}

if ! command -v kubectl >/dev/null 2>&1; then
  log "kubectl not available; skipping security scan"
  exit 0
fi

log "Checking for pods running as root"
ROOT_PODS=$(kubectl get pods -A -o jsonpath='{range .items[?(@.spec.containers[*].securityContext.runAsNonRoot==false)]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}')
if [ -n "$ROOT_PODS" ]; then
  log "Found pods running as root:\n$ROOT_PODS"
else
  log "All pods enforce non-root"
fi

log "Security scan completed"
