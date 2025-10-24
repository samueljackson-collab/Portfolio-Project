#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

npm install

pre-commit install

echo "Setup complete. Activate venv with 'source .venv/bin/activate'."
