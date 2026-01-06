# IAM Policy Configuration

This directory contains IAM policy templates for GitHub Actions CI/CD workflows.

## Files

- `github_actions_ci_policy.json.template` - Template with placeholders for AWS account-specific values
- `configure-iam-policy.sh` - Script to generate actual policy from template
- `github_oidc_trust_policy.json` - OIDC trust policy for GitHub Actions
- `policy-config.example.json` - Example configuration file

## Quick Start

### Option 1: Interactive Configuration (Recommended)

Run the configuration script to generate your IAM policy:

```bash
./configure-iam-policy.sh
```

The script will:
1. Auto-detect your AWS account ID (if AWS CLI is configured)
2. Prompt for required values:
   - AWS region
   - S3 bucket name for Terraform state
   - DynamoDB table name for state locking
   - Project name
3. Generate `github_actions_ci_policy.json` with your values

### Option 2: Manual Configuration

1. Copy the template:
   ```bash
   cp github_actions_ci_policy.json.template github_actions_ci_policy.json
   ```

2. Replace the following placeholders in `github_actions_ci_policy.json`:
   - `${TFSTATE_BUCKET_NAME}` - Your S3 bucket for Terraform state
   - `${AWS_REGION}` - Your AWS region (e.g., us-east-1)
   - `${AWS_ACCOUNT_ID}` - Your AWS account ID
   - `${TFSTATE_LOCK_TABLE}` - Your DynamoDB table for state locking
   - `${PROJECT_NAME}` - Your project name prefix

## Creating the IAM Policy in AWS

After generating the policy file, create it in AWS:

```bash
aws iam create-policy \
  --policy-name GitHubActionsCI \
  --policy-document file://github_actions_ci_policy.json
```

## Attaching the Policy

### For IAM Users
```bash
aws iam attach-user-policy \
  --user-name github-actions \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GitHubActionsCI
```

### For IAM Roles (Recommended for OIDC)
```bash
aws iam attach-role-policy \
  --role-name github-actions-role \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GitHubActionsCI
```

## Security Best Practices

1. **Never commit generated policies** - The `.gitignore` file excludes `github_actions_ci_policy.json`
2. **Use OIDC for GitHub Actions** - Prefer federated identity over static credentials
3. **Apply least privilege** - Review and restrict permissions as needed
4. **Enable CloudTrail** - Monitor IAM policy usage
5. **Rotate credentials regularly** - If using IAM user credentials

## Permissions Included

This policy grants permissions for:
- ✅ Terraform state management (S3, DynamoDB)
- ✅ VPC and networking management
- ✅ EC2 instance management
- ✅ Load balancer management
- ✅ RDS database management
- ✅ EKS cluster management
- ✅ IAM role management (scoped to project)
- ✅ S3 bucket management (scoped to project)
- ✅ CloudWatch logs and metrics
- ✅ Secrets Manager
- ✅ Lambda functions
- ✅ ECR repositories

## Troubleshooting

### Script fails to detect AWS account ID
Ensure AWS CLI is configured:
```bash
aws configure
aws sts get-caller-identity
```

### Permission denied when running script
Make the script executable:
```bash
chmod +x configure-iam-policy.sh
```

### Policy validation errors
Validate JSON syntax:
```bash
cat github_actions_ci_policy.json | jq .
```

## References

- [AWS IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform Backend Configuration](https://www.terraform.io/docs/language/settings/backends/s3.html)
