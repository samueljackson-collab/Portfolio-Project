#!/usr/bin/env bash
usage() {
  cat <<'USAGE'
Creates S3 bucket (with versioning/encryption) and DynamoDB table for Terraform remote state lock.

Usage:
  AWS_PROFILE=deploy ./scripts/bootstrap_remote_state.sh <bucket-name> [dynamodb-table] [region]

Arguments:
  bucket-name     Required. Must be lower-case letters, numbers, or hyphens (3-63 chars).
  dynamodb-table  Optional. Defaults to "twisted-monk-terraform-locks".
  region          Optional. Defaults to "us-east-1".
USAGE
}

set -euo pipefail

if [[ $# -lt 1 ]] || [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
  usage
  exit 1
fi

BUCKET_NAME="$1"
DDB_TABLE="${2:-twisted-monk-terraform-locks}"
REGION="${3:-us-east-1}"

if [[ ! "${BUCKET_NAME}" =~ ^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$ ]]; then
  echo "Error: Bucket name '${BUCKET_NAME}' is invalid. Use only lowercase letters, numbers, or hyphens (3-63 chars, cannot start/end with hyphen)." >&2
  exit 1
fi

echo "Bootstrapping remote state in region ${REGION}"
echo "Bucket: ${BUCKET_NAME}"
echo "DynamoDB table: ${DDB_TABLE}"

# Check if bucket exists
if aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
  echo "Bucket ${BUCKET_NAME} already exists"
else
  if [ "${REGION}" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "${BUCKET_NAME}" --region "${REGION}"
  else
    aws s3api create-bucket --bucket "${BUCKET_NAME}" --region "${REGION}" --create-bucket-configuration LocationConstraint="${REGION}"
  fi

  echo "Enabling versioning and default encryption"
  aws s3api put-bucket-versioning --bucket "${BUCKET_NAME}" --versioning-configuration Status=Enabled
  aws s3api put-bucket-encryption --bucket "${BUCKET_NAME}" \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
fi

# Create DynamoDB table for locking (if not exists)
if aws dynamodb describe-table --table-name "${DDB_TABLE}" --region "${REGION}" >/dev/null 2>&1; then
  echo "DynamoDB table ${DDB_TABLE} already exists"
else
  aws dynamodb create-table \
    --table-name "${DDB_TABLE}" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "${REGION}"
  echo "Waiting for DDB table to become active..."
  aws dynamodb wait table-exists --table-name "${DDB_TABLE}" --region "${REGION}"
fi

echo "Bootstrap complete. Update terraform/variables.tf with:"
echo "  tfstate_bucket = \"${BUCKET_NAME}\""
echo "  tfstate_lock_table = \"${DDB_TABLE}\""
