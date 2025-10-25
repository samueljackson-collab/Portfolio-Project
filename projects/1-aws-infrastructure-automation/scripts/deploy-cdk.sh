#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT=${1:-dev}
CDK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../cdk && pwd)"

log() {
  printf '🚀 %s\n' "$1"
}

ensure_prereqs() {
  command -v cdk >/dev/null 2>&1 || {
    echo "The AWS CDK CLI is required for this operation." >&2
    exit 1
  }
  command -v python3 >/dev/null 2>&1 || {
    echo "Python 3 must be installed for the CDK app." >&2
    exit 1
  }
}

install_deps() {
  cd "${CDK_DIR}"
  if [[ ! -d .venv ]]; then
    log "Creating virtual environment"
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt >/dev/null
}

deploy_stack() {
  cd "${CDK_DIR}"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  log "Bootstrapping environment"
  cdk bootstrap --context environment="${ENVIRONMENT}"
  log "Synthesising"
  cdk synth --context environment="${ENVIRONMENT}"
  log "Deploying stack"
  cdk deploy --require-approval never --context environment="${ENVIRONMENT}"
}

ensure_prereqs
install_deps
deploy_stack
