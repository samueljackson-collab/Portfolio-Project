#!/bin/bash
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH" uvicorn chatbot_service:app --app-dir "$PROJECT_ROOT/src" --host 0.0.0.0 --port 8000
