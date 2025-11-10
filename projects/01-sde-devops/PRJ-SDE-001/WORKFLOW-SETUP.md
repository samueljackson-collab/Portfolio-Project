# GitHub Actions Setup · Terraform Database Pipeline

Follow this checklist to enable the Terraform CI/CD workflows committed in `.github/workflows/`.

## 1. Repository Secrets
Configure the following secrets under **Settings → Secrets and variables → Actions → Repository secrets**:

| Secret | Description |
|--------|-------------|
| `AWS_TERRAFORM_ROLE_ARN` | IAM role ARN assumed by the workflows for AWS access. |
| `SLACK_BOT_TOKEN` | Bot token used by Slack notification steps. |
| `SLACK_CHANNEL_ID` | Slack channel ID (e.g., `C0123456789`). |
| `INFRACOST_API_KEY` | API key for cost estimates posted by Infracost. |

## 2. Repository Variables
Set repository-level variables for reusable values:

| Variable | Example | Purpose |
|----------|---------|---------|
| `AWS_REGION` | `us-west-2` | Default deployment region. |
| `STATE_BUCKET` | `terraform-state-prod` | Remote state bucket. |
| `STATE_LOCK_TABLE` | `terraform-locks` | DynamoDB lock table. |

## 3. GitHub Environments
Create the following environments to enforce approvals:

- **development** – No reviewers required. Map to non-production workspaces.
- **staging** – Require one reviewer approval. Used by the `plan` job.
- **production** – Require two reviewer approvals. Associate with Terraform apply job. Add Slack webhook or on-call instructions in environment secrets if desired.

For each environment, set environment secrets if values differ per stage (e.g., `SLACK_CHANNEL_ID` pointing to stage-specific channel).

## 4. Branch Protection
Enable branch protection on `main` with:
- Require pull request reviews (minimum 1).
- Require status checks to pass (select `Terraform CI/CD / Validate` and `Terraform CI/CD / Plan`).
- Require conversation resolution before merge.

## 5. Terraform State Permissions
Update the IAM policy attached to `AWS_TERRAFORM_ROLE_ARN` to include:
- `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` on the remote state bucket prefix `database/*`.
- `dynamodb:PutItem`, `dynamodb:DeleteItem`, `dynamodb:UpdateItem`, `dynamodb:GetItem` on the lock table.
- `rds:*` permissions necessary for plan/apply/destroy.
- `ec2:Describe*` permissions for networking data sources.

## 6. Slack App Configuration
- Create a Slack app with `chat:write` scope.
- Install the app to the workspace and invite it to the target channel.
- Store bot token as `SLACK_BOT_TOKEN` and channel ID as `SLACK_CHANNEL_ID`.

## 7. Infracost Integration
- Generate an API key via `https://dashboard.infracost.io`.
- Store it as `INFRACOST_API_KEY` secret.
- Optionally configure Infracost to post summary comments by enabling the GitHub App.

## 8. Drift Detection Issue Template
- Ensure `reports/drift-template.md` remains updated with remediation instructions.
- Enable Issues in the repository (Settings → General → Features).

## 9. Workflow Testing
Run the following manual checks after configuration:
1. Trigger `Terraform CI/CD` workflow via workflow dispatch with `action=plan` and `environment=dev`.
2. Open a test pull request to verify plan comment and cost estimate.
3. Manually approve the production environment and observe `apply` job waiting for reviewers.
4. Trigger `Terraform Drift Detection` via workflow dispatch to confirm issue creation and Slack alert.

Document any deviations or environment-specific overrides in this file to keep future maintainers aligned.
