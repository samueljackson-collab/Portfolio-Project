#!/usr/bin/env bash
set -euo pipefail

: "${BACKUP_ROOT:=./backups}"
: "${BACKUP_RETENTION_DAYS:=14}"

find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d -mtime "+${BACKUP_RETENTION_DAYS}" -print -exec rm -rf {} \;

if [[ -n "${S3_BUCKET:-}" ]]; then
  python3 - <<'PY'
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

bucket = os.environ["S3_BUCKET"]
prefix = os.environ.get("S3_PREFIX", "postgresql/backups")
retention_days = int(os.environ.get("BACKUP_RETENTION_DAYS", "14"))
cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

cmd = [
    "aws",
    "s3api",
    "list-objects-v2",
    "--bucket",
    bucket,
    "--prefix",
    prefix,
]
result = subprocess.run(cmd, capture_output=True, text=True, check=False)
if result.returncode != 0:
    raise SystemExit(result.stderr.strip())

payload = json.loads(result.stdout)
objects = payload.get("Contents", [])
expired = [obj["Key"] for obj in objects if datetime.fromisoformat(obj["LastModified"].replace("Z", "+00:00")) < cutoff]

for key in expired:
    subprocess.run(["aws", "s3api", "delete-object", "--bucket", bucket, "--key", key], check=True)
    print(f"Deleted s3://{bucket}/{key}")
PY
fi

