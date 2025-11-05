#!/usr/bin/env bash
# Creates S3 bucket (with versioning/encryption) and DynamoDB table for Terraform remote state.
#
# Usage:
#   ./scripts/bootstrap_remote_state.sh [bucket-name] [dynamodb-table] [region]
#
# Examples:
#   # Use auto-generated bucket name with account ID suffix
#   ./scripts/bootstrap_remote_state.sh
#
#   # Specify custom bucket name
#   ./scripts/bootstrap_remote_state.sh my-custom-tfstate-bucket
#
#   # Specify all parameters
#   AWS_PROFILE=deploy ./scripts/bootstrap_remote_state.sh my-bucket my-lock-table us-west-2

set -euo pipefail

# Get AWS account ID for generating unique bucket name
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "UNKNOWN")

# Use account ID in default bucket name to ensure global uniqueness
DEFAULT_BUCKET="twisted-monk-tfstate-${ACCOUNT_ID}"

BUCKET_NAME="${1:-$DEFAULT_BUCKET}"
DDB_TABLE="${2:-twisted-monk-terraform-locks}"
REGION="${3:-us-east-1}"

echo "=========================================="
echo "Terraform Remote State Bootstrap"
echo "=========================================="
echo "AWS Account: ${ACCOUNT_ID}"
echo "Region:      ${REGION}"
echo "S3 Bucket:   ${BUCKET_NAME}"
echo "DynamoDB:    ${DDB_TABLE}"
echo "=========================================="
echo ""

# Check if bucket exists
if aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
  echo "✓ S3 bucket ${BUCKET_NAME} already exists"
else
  echo "Creating S3 bucket ${BUCKET_NAME}..."
  if [ "${REGION}" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "${BUCKET_NAME}" --region "${REGION}"
  else
    aws s3api create-bucket \
      --bucket "${BUCKET_NAME}" \
      --region "${REGION}" \
      --create-bucket-configuration LocationConstraint="${REGION}"
  fi

  echo "Enabling versioning on ${BUCKET_NAME}..."
  aws s3api put-bucket-versioning \
    --bucket "${BUCKET_NAME}" \
    --versioning-configuration Status=Enabled

  echo "Enabling server-side encryption on ${BUCKET_NAME}..."
  aws s3api put-bucket-encryption \
    --bucket "${BUCKET_NAME}" \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"},"BucketKeyEnabled":true}]}'

  echo "Enabling public access block on ${BUCKET_NAME}..."
  aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

  echo "✓ S3 bucket created and configured"
fi

# Create DynamoDB table for state locking
if aws dynamodb describe-table --table-name "${DDB_TABLE}" --region "${REGION}" >/dev/null 2>&1; then
  echo "✓ DynamoDB table ${DDB_TABLE} already exists"
else
  echo "Creating DynamoDB table ${DDB_TABLE}..."
  aws dynamodb create-table \
    --table-name "${DDB_TABLE}" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "${REGION}" \
    --tags Key=Purpose,Value=TerraformStateLock Key=ManagedBy,Value=bootstrap-script

  echo "Waiting for DynamoDB table to become active..."
  aws dynamodb wait table-exists --table-name "${DDB_TABLE}" --region "${REGION}"
  echo "✓ DynamoDB table created"
fi

echo ""
echo "=========================================="
echo "✓ Bootstrap Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Initialize Terraform with backend config:"
echo "   cd terraform"
echo "   terraform init \\"
echo "     -backend-config=\"bucket=${BUCKET_NAME}\" \\"
echo "     -backend-config=\"region=${REGION}\" \\"
echo "     -backend-config=\"dynamodb_table=${DDB_TABLE}\""
echo ""
echo "2. OR create a backend.hcl file:"
echo "   cat > terraform/backend.hcl <<EOL"
echo "   bucket         = \"${BUCKET_NAME}\""
echo "   region         = \"${REGION}\""
echo "   dynamodb_table = \"${DDB_TABLE}\""
echo "   EOL"
echo ""
echo "   Then run: terraform init -backend-config=backend.hcl"
echo ""
echo "3. For GitHub Actions, set these secrets:"
echo "   AWS_REGION:      ${REGION}"
echo "   TFSTATE_BUCKET:  ${BUCKET_NAME}"
echo "=========================================="