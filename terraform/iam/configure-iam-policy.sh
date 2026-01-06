#!/bin/bash
# Configure IAM policy template
# This script processes the IAM policy template and replaces placeholders with actual values

set -e

echo "=================================================="
echo " GitHub Actions IAM Policy Configuration"
echo "=================================================="
echo ""

# Get AWS account ID
echo "Fetching AWS account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")

if [ -z "$ACCOUNT_ID" ]; then
  echo "⚠️  Could not auto-detect AWS account ID. You'll need to provide it manually."
  read -p "Enter AWS account ID: " ACCOUNT_ID
else
  echo "✓ Detected AWS account ID: $ACCOUNT_ID"
fi

# Get AWS region
read -p "Enter AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Prompt for values
read -p "Enter tfstate S3 bucket name: " BUCKET_NAME
read -p "Enter DynamoDB table name for state locking: " TABLE_NAME
read -p "Enter project name (default: portfolio-project): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-portfolio-project}

# Validate inputs
if [ -z "$BUCKET_NAME" ] || [ -z "$TABLE_NAME" ] || [ -z "$ACCOUNT_ID" ]; then
  echo "❌ Error: Bucket name, table name, and account ID are required"
  exit 1
fi

echo ""
echo "Configuration:"
echo "  AWS Account ID: $ACCOUNT_ID"
echo "  AWS Region: $AWS_REGION"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  DynamoDB Table: $TABLE_NAME"
echo "  Project Name: $PROJECT_NAME"
echo ""
read -p "Generate IAM policy with these values? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
  echo "Aborted"
  exit 0
fi

# Process template
echo ""
echo "Processing template..."

sed "s/\${TFSTATE_BUCKET_NAME}/$BUCKET_NAME/g" \
    github_actions_ci_policy.json.template | \
sed "s/\${AWS_REGION}/$AWS_REGION/g" | \
sed "s/\${AWS_ACCOUNT_ID}/$ACCOUNT_ID/g" | \
sed "s/\${TFSTATE_LOCK_TABLE}/$TABLE_NAME/g" | \
sed "s/\${PROJECT_NAME}/$PROJECT_NAME/g" \
    > github_actions_ci_policy.json

echo "✓ Policy configured: github_actions_ci_policy.json"

echo ""
echo "=================================================="
echo "✓ Configuration complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Review the generated policy: cat github_actions_ci_policy.json"
echo "  2. Create the policy in AWS:"
echo "     aws iam create-policy \\"
echo "       --policy-name GitHubActionsCI \\"
echo "       --policy-document file://github_actions_ci_policy.json"
echo "  3. Attach the policy to your GitHub Actions role/user"
echo ""
