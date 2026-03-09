#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)

if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${PROJECT_ROOT}/.env"
  set +a
fi

BACKUP_DIR=${BACKUP_DIR:-${PROJECT_ROOT}/backups}
BACKUP_FORMAT=${BACKUP_FORMAT:-custom}
BACKUP_COMPRESS_LEVEL=${BACKUP_COMPRESS_LEVEL:-6}
S3_BUCKET=${S3_BUCKET:-}
S3_PREFIX=${S3_PREFIX:-postgresql-backups}
S3_SSE=${S3_SSE:-AES256}

mkdir -p "${BACKUP_DIR}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${PGDATABASE}_${TIMESTAMP}.dump"

pg_dump \
  --format="${BACKUP_FORMAT}" \
  --compress="${BACKUP_COMPRESS_LEVEL}" \
  --file="${BACKUP_FILE}"

echo "Backup created: ${BACKUP_FILE}"

if [[ -n "${S3_BUCKET}" ]]; then
  if ! command -v aws >/dev/null 2>&1; then
    echo "AWS CLI not found. Skipping S3 upload." >&2
    exit 0
  fi
  aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/${S3_PREFIX}/" --sse "${S3_SSE}"
  echo "Uploaded to s3://${S3_BUCKET}/${S3_PREFIX}/"
fi
