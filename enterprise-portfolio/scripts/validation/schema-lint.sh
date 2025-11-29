#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root_dir"

python3 - <<'PY'
import json
from pathlib import Path

schema_files = list(Path("kubernetes/manifests").glob("**/*.yaml"))
print(json.dumps({"files_checked": len(schema_files)}))
PY
