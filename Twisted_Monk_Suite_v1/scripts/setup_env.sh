#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f "Twisted_Monk_Suite_v1/.env" ]]; then
  cp Twisted_Monk_Suite_v1/.env.example Twisted_Monk_Suite_v1/.env
  echo "Created Twisted_Monk_Suite_v1/.env from template"
fi

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r Twisted_Monk_Suite_v1/backend/requirements.txt

echo "Environment ready. Activate with 'source .venv/bin/activate'"
