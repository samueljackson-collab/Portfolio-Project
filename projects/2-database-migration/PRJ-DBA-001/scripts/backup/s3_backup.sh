#!/usr/bin/env bash
set -euo pipefail

backup_path="${1:-}"

if [[ -z "${backup_path}" ]]; then
  echo "Usage: $0 <backup_path>" >&2
  exit 1
fi

: "${S3_BUCKET:?S3_BUCKET is required}"
: "${S3_PREFIX:=postgresql/backups}"
: "${S3_SSE_ALGORITHM:=AES256}"

if [[ ! -f "${backup_path}" ]]; then
  echo "Backup file not found: ${backup_path}" >&2
  exit 1
fi

s3_key="${S3_PREFIX}/$(basename "${backup_path}")"

if [[ "${S3_SSE_ALGORITHM}" == "aws:kms" ]]; then
  aws s3 cp "${backup_path}" "s3://${S3_BUCKET}/${s3_key}" \
    --sse aws:kms \
    --sse-kms-key-id "${S3_KMS_KEY_ID:-}"
else
  aws s3 cp "${backup_path}" "s3://${S3_BUCKET}/${s3_key}" \
    --sse "${S3_SSE_ALGORITHM}"
fi

echo "Uploaded ${backup_path} to s3://${S3_BUCKET}/${s3_key}"
