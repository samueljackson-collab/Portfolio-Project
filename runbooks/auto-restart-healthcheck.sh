#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-app}"        # systemd unit or kubectl deployment name
HEALTH_URL="${HEALTH_URL:-http://localhost:8080/healthz}"
TIMEOUT="${TIMEOUT:-5}"
RETRIES="${RETRIES:-3}"
SLEEP="${SLEEP:-5}"

log() { echo "$(date -Is) $*"; }

check_health() {
  curl -fsS --max-time "${TIMEOUT}" "${HEALTH_URL}" >/dev/null
}

restart_service() {
  if command -v systemctl >/dev/null; then
    log "Restarting systemd service ${SERVICE_NAME}" && sudo systemctl restart "${SERVICE_NAME}"
  elif command -v kubectl >/dev/null; then
    log "Restarting Kubernetes deployment ${SERVICE_NAME}" && kubectl rollout restart deployment "${SERVICE_NAME}"
  else
    log "No restart mechanism available for ${SERVICE_NAME}" && return 1
  fi
}

attempt=0
until check_health; do
  attempt=$((attempt + 1))
  log "Health check failed for ${HEALTH_URL} (attempt ${attempt}/${RETRIES})"
  if [[ ${attempt} -ge ${RETRIES} ]]; then
    log "Threshold reached; triggering restart"
    restart_service || log "Restart failed"
    attempt=0
  fi
  sleep "${SLEEP}"
done

log "Service ${SERVICE_NAME} healthy at ${HEALTH_URL}"
