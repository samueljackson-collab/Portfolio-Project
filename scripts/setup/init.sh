#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[SETUP] %s\n' "$*"
}

log "Creating Python virtual environment"
python3 -m venv .venv

log "Installing Node dependencies"
if [ -f package.json ]; then
  npm install
else
  log "No package.json found, skipping"
fi

log "Setup complete"
