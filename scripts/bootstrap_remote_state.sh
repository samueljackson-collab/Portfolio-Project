#!/usr/bin/env bash
# Creates S3 bucket (with versioning/encryption) and DynamoDB table for Terraform remote state lock.
# Usage:
#   AWS_PROFILE=deploy ./scripts/bootstrap_remote_state.sh <bucket-name> <dynamodb-table> <region>

set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"

log_dry_run() {
  if [[ "${DRY_RUN}" != "1" ]]; then
    return
  fi

  printf '[DRY RUN]'
  for arg in "$@"; do
    printf ' %q' "$arg"
  done
  printf '\n'
}

ensure_aws_cli() {
  if command -v aws >/dev/null 2>&1; then
    return
  fi

  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "[DRY RUN] aws CLI not found. Commands will be simulated." >&2
    return
  fi

  echo "Error: aws CLI is required" >&2
  exit 1
}

aws_cli() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    log_dry_run aws "$@"
    return 0
  fi
  aws "$@"
}

aws_check() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    log_dry_run aws "$@"
    return 1
  fi
  aws "$@"
}

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "Dry run mode enabled. No changes will be made."
fi

ensure_aws_cli

BUCKET_NAME="${1:-twisted-monk-terraform-state-REPLACE_ME}"
DDB_TABLE="${2:-twisted-monk-terraform-locks}"
REGION="${3:-us-east-1}"

echo "Bootstrapping remote state in region ${REGION}"
echo "Bucket: ${BUCKET_NAME}"
echo "DynamoDB table: ${DDB_TABLE}"

# Check if bucket exists
if aws_check s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
  echo "Bucket ${BUCKET_NAME} already exists"
else
  if [ "${REGION}" = "us-east-1" ]; then
    aws_cli s3api create-bucket --bucket "${BUCKET_NAME}" --region "${REGION}"
  else
    aws_cli s3api create-bucket --bucket "${BUCKET_NAME}" --region "${REGION}" --create-bucket-configuration LocationConstraint="${REGION}"
  fi

  echo "Enabling versioning and default encryption"
  aws_cli s3api put-bucket-versioning --bucket "${BUCKET_NAME}" --versioning-configuration Status=Enabled
  aws_cli s3api put-bucket-encryption --bucket "${BUCKET_NAME}" \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
fi

# Create DynamoDB table for locking (if not exists)
if aws_check dynamodb describe-table --table-name "${DDB_TABLE}" --region "${REGION}" >/dev/null 2>&1; then
  echo "DynamoDB table ${DDB_TABLE} already exists"
else
  aws_cli dynamodb create-table \
    --table-name "${DDB_TABLE}" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "${REGION}"
  echo "Waiting for DDB table to become active..."
  aws_cli dynamodb wait table-exists --table-name "${DDB_TABLE}" --region "${REGION}"
fi

echo "Bootstrap complete. Update terraform/variables.tf with:"
echo "  tfstate_bucket = \"${BUCKET_NAME}\""
echo "  tfstate_lock_table = \"${DDB_TABLE}\""
