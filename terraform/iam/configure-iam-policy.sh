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
  read -r -p "Enter AWS account ID: " ACCOUNT_ID
else
  echo "✓ Detected AWS account ID: $ACCOUNT_ID"
fi

# Get AWS region
read -r -p "Enter AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Prompt for values
read -r -p "Enter tfstate S3 bucket name: " BUCKET_NAME
read -r -p "Enter DynamoDB table name for state locking: " TABLE_NAME
read -r -p "Enter project name (default: portfolio-project): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-portfolio-project}

# Validate inputs
if [ -z "$BUCKET_NAME" ] || [ -z "$TABLE_NAME" ] || [ -z "$ACCOUNT_ID" ] || [ -z "$AWS_REGION" ]; then
  echo "❌ Error: Bucket name, table name, account ID, and region are required"
  exit 1
fi

# Validate AWS region format
if ! echo "$AWS_REGION" | grep -qE '^[a-z]{2}-[a-z]+-[0-9]{1}$'; then
  echo "❌ Error: Invalid AWS region format. Expected format like 'us-east-1'"
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
read -r -p "Generate IAM policy with these values? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
  echo "Aborted"
  exit 0
fi

# Process template
echo ""
echo "Processing template..."

# Escape special characters for sed (/, &, \)
escape_sed() {
  echo "$1" | sed 's/[\/&]/\\&/g'
}

BUCKET_NAME_ESCAPED=$(escape_sed "$BUCKET_NAME")
AWS_REGION_ESCAPED=$(escape_sed "$AWS_REGION")
ACCOUNT_ID_ESCAPED=$(escape_sed "$ACCOUNT_ID")
TABLE_NAME_ESCAPED=$(escape_sed "$TABLE_NAME")
PROJECT_NAME_ESCAPED=$(escape_sed "$PROJECT_NAME")

sed "s/\${TFSTATE_BUCKET_NAME}/$BUCKET_NAME_ESCAPED/g" \
    github_actions_ci_policy.json.template | \
sed "s/\${AWS_REGION}/$AWS_REGION_ESCAPED/g" | \
sed "s/\${AWS_ACCOUNT_ID}/$ACCOUNT_ID_ESCAPED/g" | \
sed "s/\${TFSTATE_LOCK_TABLE}/$TABLE_NAME_ESCAPED/g" | \
sed "s/\${PROJECT_NAME}/$PROJECT_NAME_ESCAPED/g" \
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
