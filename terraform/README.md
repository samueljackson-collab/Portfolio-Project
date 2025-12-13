# Terraform Infrastructure Stack

Modular Terraform configuration for VPC networking, application primitives (S3, RDS, optional EKS control plane), and monitoring/alerting. The stack is split into three modules under `terraform/modules` and orchestrated by the root `main.tf`.

## Modules
- **VPC**: Creates VPC, public/private subnets, route tables, optional NAT gateway, and exposes subnet IDs for workloads.
- **App**: Provisions an encrypted S3 asset bucket, optional PostgreSQL RDS instance, and (optionally) an EKS control plane for Kubernetes workloads.
- **Monitoring**: Enables VPC flow logs, provisions CloudWatch log groups/roles, and creates SNS-backed CloudWatch alarms for RDS CPU utilization.

## Prerequisites
- Terraform >= 1.0 and AWS CLI installed.
- An AWS account with permissions to create networking, IAM, RDS, and CloudWatch resources.
- Remote state bucket and DynamoDB lock table (bootstrap with `./scripts/bootstrap_remote_state.sh <project> <region>`). Update the `backend.tf` block with the emitted bucket/table names.
- GitHub secrets (for CI): `AWS_REGION`, `TFSTATE_BUCKET`, `TFSTATE_DDB_TABLE`, `AWS_ROLE_ARN_PLAN`, `AWS_ROLE_ARN_APPLY` (for OIDC), or legacy access keys if OIDC is not yet configured.

## Deployment
1. Set environment variables or update `terraform/variables.tf` for CIDRs, database settings, and alert destinations.
2. Initialize: `terraform init -backend-config="bucket=$TFSTATE_BUCKET" -backend-config="region=$AWS_REGION" -backend-config="dynamodb_table=$TFSTATE_DDB_TABLE"`.
3. Review: `terraform plan -var "aws_region=$AWS_REGION" -var "alarm_email=you@example.com"`.
4. Apply: `terraform apply` (or via GitHub Actions with environment approval).

> **Tip:** Use workspaces (`terraform workspace new stage`) to isolate environments; the module tags include the workspace/environment name automatically.

## Security
- S3 buckets block public access, enable versioning, and enforce SSE (AES256).
- RDS is private-only, password can be generated if omitted, and security groups restrict access to the VPC CIDR.
- VPC flow logs are enabled by default for auditing; IAM roles are scoped to required CloudWatch actions.
- GitHub Actions are designed for OIDC (short-lived credentials). Protect the `production` environment to require manual approval for applies.

## Cost Awareness
- NAT Gateway is optional (`enable_nat_gateway=false`) to reduce egress costs in lower environments.
- RDS creation is toggled by `create_rds`; disable for dev sandboxes or use smaller instance classes/storage.
- Flow logs retention is configurable (`flow_log_retention_days`) to balance auditability and storage spend.
- EKS control plane is off by default; enable only when Kubernetes workloads are required.

## Outputs
Key outputs include VPC identifiers, subnet IDs, NAT/IGW IDs, S3 bucket name, RDS endpoint, EKS cluster name, flow log group, and SNS topic ARN (see `outputs.tf`).

## Examples
A ready-to-run example lives in `terraform/examples/complete`:
```bash
cd terraform/examples/complete
terraform init
terraform plan
```

## CI/CD
GitHub Actions (`.github/workflows/terraform.yml`) runs `terraform fmt`, `validate`, `tfsec`, and `tflint`, produces a plan on pull requests, and requires environment approval before applying to `main`.

For OIDC role creation steps, refer to `terraform/iam/github_oidc_trust_policy.json` and `terraform/iam/github_actions_ci_policy.json`.
