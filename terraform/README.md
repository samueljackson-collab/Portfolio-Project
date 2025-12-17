# Infrastructure Deployment (Twisted Monk Suite)

This directory contains Terraform templates & scripts to deploy infrastructure.

Quick start:

1. Install dependencies: Terraform, AWS CLI (or provider CLI).
2. Bootstrap remote state:
   ./scripts/bootstrap_remote_state.sh <tfstate-bucket> <dynamodb-table> <region>
3. Update terraform/variables.tf with the bucket/table names (or set TF_VAR_* env vars).
4. Run locally:
   ./scripts/deploy.sh <workspace> [auto-approve]
5. Use GitHub Actions to run plan & apply (configure secrets: AWS_REGION, TFSTATE_BUCKET, AWS_ROLE_ARN_PLAN, AWS_ROLE_ARN_APPLY).

Security:

- Use OIDC where possible: configure GitHub Action OIDC and an IAM role for the GitHub repo.
- Never commit secrets into the repo. Use GitHub Secrets or Vault.
- Ensure the S3 state bucket has versioning & SSE enabled.

## Using GitHub OIDC for CI

GitHub Actions can authenticate to AWS using OpenID Connect (OIDC) instead of long-lived access keys. This is the recommended approach for improved security.

### Prerequisites

1. An AWS account with permissions to create IAM roles and OIDC providers
2. The GitHub repository where you'll run Terraform workflows
3. AWS CLI configured with admin credentials (for initial setup)

### Step 1: Create the OIDC Identity Provider in AWS

First, create an OIDC identity provider in your AWS account that trusts GitHub Actions:

```bash
# Create the OIDC provider (only needs to be done once per AWS account)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Note:** If the OIDC provider already exists in your account, you can skip this step.

### Step 2: Create the IAM Role with Trust Policy

Create an IAM role that GitHub Actions can assume. Use the trust policy template provided in `terraform/iam/github_oidc_trust_policy.json`:

```bash
# Replace placeholders in the trust policy
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export GITHUB_REPO="samueljackson-collab/Portfolio-Project"  # Replace with your repo

# Create a temporary trust policy file with values substituted
cat terraform/iam/github_oidc_trust_policy.json | \
  sed "s/REPLACE_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" | \
  sed "s/\${{ github.repository }}/$GITHUB_REPO/g" > /tmp/trust_policy.json

# Create the IAM role
aws iam create-role \
  --role-name GitHubActionsRole-TerraformCI \
  --assume-role-policy-document file:///tmp/trust_policy.json \
  --description "Role for GitHub Actions to run Terraform CI/CD"

# Get the role ARN (save this for later)
aws iam get-role \
  --role-name GitHubActionsRole-TerraformCI \
  --query 'Role.Arn' \
  --output text
```

**Important:** The trust policy restricts access to the `main` branch. To allow other branches or tags, modify the `Condition` in the trust policy JSON:

```json
"Condition": {
  "StringLike": {
    "token.actions.githubusercontent.com:sub": [
      "repo:OWNER/REPO:ref:refs/heads/main",
      "repo:OWNER/REPO:ref:refs/heads/infra/*",
      "repo:OWNER/REPO:ref:refs/tags/*"
    ]
  }
}
```

### Step 3: Attach the CI Policy to the Role

Attach the least-privilege policy that grants Terraform the permissions it needs:

```bash
# Replace placeholders in the CI policy
export TFSTATE_BUCKET="your-terraform-state-bucket"  # Replace with your bucket name
export DDB_TABLE="your-terraform-lock-table"         # Replace with your DynamoDB table name

# Create a temporary policy file with values substituted
cat terraform/iam/github_actions_ci_policy.json | \
  sed "s/REPLACE_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" | \
  sed "s/REPLACE_TFSTATE_BUCKET/$TFSTATE_BUCKET/g" | \
  sed "s/REPLACE_DDB_TABLE/$DDB_TABLE/g" | \
  sed "s/\${{ AWS_REGION }}/*/g" > /tmp/ci_policy.json

# Create the policy
aws iam create-policy \
  --policy-name GitHubActionsTerraformCI \
  --policy-document file:///tmp/ci_policy.json \
  --description "Least-privilege policy for Terraform CI/CD via GitHub Actions"

# Attach the policy to the role
export POLICY_ARN=$(aws iam list-policies --query 'Policies[?PolicyName==`GitHubActionsTerraformCI`].Arn' --output text)
aws iam attach-role-policy \
  --role-name GitHubActionsRole-TerraformCI \
  --policy-arn $POLICY_ARN
```

**Security Note:** The provided policy is intentionally broad for initial bootstrap. Before production use, tighten resource ARNs to specific resources:

```json
"Resource": [
  "arn:aws:ec2:us-east-1:123456789012:vpc/vpc-abc123",
  "arn:aws:rds:us-east-1:123456789012:db:my-database"
]
```

### Step 4: Configure GitHub Secrets

Add the role ARN to your GitHub repository secrets:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AWS_ROLE_ARN_PLAN`: The ARN of the role created above (for plan operations)
   - `AWS_ROLE_ARN_APPLY`: The same ARN (or a different role with more permissions for apply)
   - `AWS_REGION`: Your AWS region (e.g., `us-east-1`)
   - `TFSTATE_BUCKET`: Your Terraform state S3 bucket name

### Step 5: Update the Workflow to Use OIDC

In `.github/workflows/terraform.yml`, uncomment the OIDC authentication steps and comment out the legacy access key authentication:

```yaml
# Uncomment this block
- name: Configure AWS credentials via OIDC
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN_PLAN }}
    aws-region: ${{ env.AWS_REGION }}
    role-session-name: GitHubActions-TerraformPlan

# Comment out the legacy authentication block
# - name: Configure AWS credentials
#   uses: aws-actions/configure-aws-credentials@v2
#   with:
#     aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
#     ...
```

### Step 6: Configure Environment Protection for Apply

To require manual approval before applying Terraform changes:

1. Go to your repository → Settings → Environments
2. Click "New environment" and name it `production`
3. Under "Environment protection rules":
   - Check "Required reviewers"
   - Add reviewers who must approve before apply runs
   - (Optional) Set a wait timer
   - (Optional) Restrict to specific branches (e.g., `main`)
4. Save the environment configuration

The workflow is already configured to use the `production` environment for the apply job.

### Testing Locally with OIDC Credentials

You can test the OIDC role locally using AWS CLI:

```bash
# Assume the role (this simulates what GitHub Actions does)
aws sts assume-role-with-web-identity \
  --role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsRole-TerraformCI \
  --role-session-name test-session \
  --web-identity-token "YOUR_OIDC_TOKEN" \
  --duration-seconds 3600

# For local development, use your normal AWS credentials or AWS SSO
# The OIDC role is specifically for GitHub Actions
```

### Verification

To verify your OIDC setup:

1. Push a change to the `infra/bootstrap-terraform` branch or create a PR
2. Check the Actions tab to see if the workflow runs successfully
3. Verify that the plan job completes without authentication errors
4. For apply, verify that it waits for manual approval in the production environment

### Troubleshooting

**"Not authorized to perform sts:AssumeRoleWithWebIdentity"**

- Verify the trust policy has the correct AWS account ID and repository name
- Ensure the OIDC provider thumbprint is correct
- Check that the branch/tag matches the condition in the trust policy

**"Access Denied" during Terraform operations**

- Review the IAM policy attached to the role
- Check CloudTrail logs for specific denied actions
- Ensure S3 bucket and DynamoDB table names are correct in the policy

**Apply job doesn't wait for approval**

- Verify the environment name in the workflow matches the environment in GitHub settings
- Ensure environment protection rules are configured with required reviewers

Testing & quality:

- terraform fmt -recursive
- terraform validate
- tflint
- checkov (static security scan)
- terratest (Go) for integration tests

Notes:

- The bootstrap script creates S3 and DynamoDB for Terraform remote state. Run it once with an admin account.
- The provided main.tf is an example. Replace/add modules for VPC, EKS, RDS, etc. per your architecture.
