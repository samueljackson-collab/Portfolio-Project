#!/usr/bin/env bash
set -euo pipefail

pip install -r requirements.txt
pip install -r backend/requirements.txt
(cd frontend && npm install)
(cd monitoring && pip install -r requirements.txt)
pre-commit install
