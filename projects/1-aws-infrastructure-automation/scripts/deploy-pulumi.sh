#!/usr/bin/env bash
set -euo pipefail

STACK=${1:-dev}
PULUMI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../pulumi && pwd)"

log() {
  printf '🌐 %s\n' "$1"
}

ensure_prereqs() {
  command -v pulumi >/dev/null 2>&1 || {
    echo "Pulumi CLI is required." >&2
    exit 1
  }
  command -v python3 >/dev/null 2>&1 || {
    echo "Python 3 is required for Pulumi." >&2
    exit 1
  }
}

install_deps() {
  cd "${PULUMI_DIR}"
  if [[ ! -d venv ]]; then
    python3 -m venv venv
  fi
  # shellcheck disable=SC1091
  source venv/bin/activate
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt >/dev/null
}

deploy_stack() {
  cd "${PULUMI_DIR}"
  # shellcheck disable=SC1091
  source venv/bin/activate
  log "Previewing ${STACK}"
  pulumi preview -s "${STACK}" || true
  log "Deploying ${STACK}"
  pulumi up -y -s "${STACK}"
}

ensure_prereqs
install_deps
deploy_stack
