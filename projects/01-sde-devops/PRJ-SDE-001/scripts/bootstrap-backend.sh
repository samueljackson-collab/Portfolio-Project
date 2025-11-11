#!/bin/bash
# =====================================================
# Terraform Backend Bootstrap Script
# =====================================================
# Creates S3 bucket and DynamoDB table for remote state
#
# Usage:
#   ./scripts/bootstrap-backend.sh [bucket-name] [region] [dynamodb-table]
#
# Example:
#   ./scripts/bootstrap-backend.sh terraform-state-prj-sde-001 us-east-1 terraform-state-lock
#
# Prerequisites:
#   - AWS CLI installed and configured
#   - IAM permissions: s3:*, dynamodb:*, kms:* (for encryption)
#
# What this script creates:
#   1. S3 bucket with versioning and encryption
#   2. DynamoDB table for state locking
#   3. Bucket policy to enforce SSL/TLS
#   4. (Optional) KMS key for encryption

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUCKET_NAME="${1:-terraform-state-prj-sde-001}"
AWS_REGION="${2:-us-east-1}"
DYNAMODB_TABLE="${3:-terraform-state-lock}"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}Terraform Backend Bootstrap${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""
echo -e "Configuration:"
echo -e "  S3 Bucket:      ${GREEN}${BUCKET_NAME}${NC}"
echo -e "  AWS Region:     ${GREEN}${AWS_REGION}${NC}"
echo -e "  DynamoDB Table: ${GREEN}${DYNAMODB_TABLE}${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI not found. Install from: https://aws.amazon.com/cli/${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS credentials not configured. Run: aws configure${NC}"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "  AWS Account:    ${GREEN}${ACCOUNT_ID}${NC}"
echo ""

# Function to check if S3 bucket exists
bucket_exists() {
    aws s3api head-bucket --bucket "$1" 2>/dev/null
}

# Function to check if DynamoDB table exists
table_exists() {
    aws dynamodb describe-table --table-name "$1" --region "$AWS_REGION" &>/dev/null
}

# =====================================================
# Step 1: Create S3 Bucket
# =====================================================
echo -e "${BLUE}Step 1: Creating S3 bucket...${NC}"

if bucket_exists "$BUCKET_NAME"; then
    echo -e "${YELLOW}⚠ S3 bucket already exists: ${BUCKET_NAME}${NC}"
else
    # Create S3 bucket
    if [ "$AWS_REGION" = "us-east-1" ]; then
        # us-east-1 doesn't support LocationConstraint
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$AWS_REGION"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION"
    fi
    echo -e "${GREEN}✓ S3 bucket created: ${BUCKET_NAME}${NC}"
fi

# =====================================================
# Step 2: Enable Versioning
# =====================================================
echo -e "${BLUE}Step 2: Enabling S3 versioning...${NC}"
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled
echo -e "${GREEN}✓ Versioning enabled${NC}"

# =====================================================
# Step 3: Enable Server-Side Encryption
# =====================================================
echo -e "${BLUE}Step 3: Enabling server-side encryption...${NC}"
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'
echo -e "${GREEN}✓ Encryption enabled (AES-256)${NC}"

# =====================================================
# Step 4: Block Public Access
# =====================================================
echo -e "${BLUE}Step 4: Blocking public access...${NC}"
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
echo -e "${GREEN}✓ Public access blocked${NC}"

# =====================================================
# Step 5: Apply Bucket Policy (Enforce SSL/TLS)
# =====================================================
echo -e "${BLUE}Step 5: Applying bucket policy...${NC}"
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EnforcedTLS",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::${BUCKET_NAME}",
                "arn:aws:s3:::${BUCKET_NAME}/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file:///tmp/bucket-policy.json
echo -e "${GREEN}✓ Bucket policy applied (SSL/TLS enforced)${NC}"
rm /tmp/bucket-policy.json

# =====================================================
# Step 6: Configure Lifecycle Policy
# =====================================================
echo -e "${BLUE}Step 6: Configuring lifecycle policy...${NC}"
cat > /tmp/lifecycle-policy.json <<EOF
{
    "Rules": [
        {
            "Id": "DeleteOldVersions",
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 90
            },
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": 7
            }
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket "$BUCKET_NAME" \
    --lifecycle-configuration file:///tmp/lifecycle-policy.json
echo -e "${GREEN}✓ Lifecycle policy configured (90-day retention)${NC}"
rm /tmp/lifecycle-policy.json

# =====================================================
# Step 7: Create DynamoDB Table for Locking
# =====================================================
echo -e "${BLUE}Step 7: Creating DynamoDB table...${NC}"

if table_exists "$DYNAMODB_TABLE"; then
    echo -e "${YELLOW}⚠ DynamoDB table already exists: ${DYNAMODB_TABLE}${NC}"
else
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --region "$AWS_REGION" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --tags Key=ManagedBy,Value=Terraform Key=Purpose,Value=StateLocking

    echo -e "${YELLOW}⏳ Waiting for table to be active...${NC}"
    aws dynamodb wait table-exists \
        --table-name "$DYNAMODB_TABLE" \
        --region "$AWS_REGION"

    echo -e "${GREEN}✓ DynamoDB table created: ${DYNAMODB_TABLE}${NC}"
fi

# =====================================================
# Step 8: Enable Point-in-Time Recovery
# =====================================================
echo -e "${BLUE}Step 8: Enabling point-in-time recovery...${NC}"
aws dynamodb update-continuous-backups \
    --table-name "$DYNAMODB_TABLE" \
    --region "$AWS_REGION" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
echo -e "${GREEN}✓ Point-in-time recovery enabled${NC}"

# =====================================================
# Summary
# =====================================================
echo ""
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}✓ Backend resources created successfully!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Update ${BLUE}infrastructure/backend.tf${NC} with these values:"
echo -e "     ${YELLOW}bucket         = \"${BUCKET_NAME}\"${NC}"
echo -e "     ${YELLOW}region         = \"${AWS_REGION}\"${NC}"
echo -e "     ${YELLOW}dynamodb_table = \"${DYNAMODB_TABLE}\"${NC}"
echo ""
echo -e "  2. Uncomment the backend block in ${BLUE}backend.tf${NC}"
echo ""
echo -e "  3. Initialize Terraform with remote backend:"
echo -e "     ${BLUE}cd infrastructure && terraform init -migrate-state${NC}"
echo ""
echo -e "  4. Verify state migration:"
echo -e "     ${BLUE}terraform state list${NC}"
echo ""
echo -e "  5. (Optional) Delete local state file after verification:"
echo -e "     ${YELLOW}rm terraform.tfstate terraform.tfstate.backup${NC}"
echo ""

# Output backend configuration for easy copy-paste
echo -e "${BLUE}Backend Configuration (add to backend.tf):${NC}"
echo -e "${YELLOW}=====================================================${NC}"
cat <<EOF
backend "s3" {
  bucket         = "${BUCKET_NAME}"
  key            = "full-stack-app/terraform.tfstate"
  region         = "${AWS_REGION}"
  dynamodb_table = "${DYNAMODB_TABLE}"
  encrypt        = true
}
EOF
echo -e "${YELLOW}=====================================================${NC}"
echo ""

echo -e "${GREEN}Bootstrap complete!${NC}"
