# Terraform Stack

Composable Terraform modules for the portfolio platform. The stack is split into VPC networking, shared application services, and monitoring primitives. Use the root configuration as a reference implementation or wire the modules into your own environments.

## Modules
- **modules/vpc**: Highly-available VPC with public/private subnets, routing, optional NAT Gateway, and VPC Flow Logs.
- **modules/app**: S3 assets bucket, application log group, and optional PostgreSQL RDS instance hardened for private subnets.
- **modules/monitoring**: SNS alert topic with email subscriptions, CloudWatch dashboard, and RDS CPU/storage alarms.

## Getting Started
1. **Install**: Terraform >= 1.0, AWS CLI, and tfsec.
2. **Bootstrap remote state** (once):
   ```bash
   ./scripts/bootstrap_remote_state.sh <project-name> <aws-region>
   ```
3. **Configure backend**: Update `backend.tf` with the S3 bucket and DynamoDB table output by the bootstrap script, then run `terraform init`.
4. **Plan/apply locally**:
   ```bash
   terraform fmt -recursive
   terraform init
   terraform validate
   terraform plan -out=tfplan
   terraform apply tfplan
   ```
5. **Try the example**: `cd terraform/examples/basic && terraform init && terraform apply`.

## Variables
Key variables are defined in `variables.tf`:
- `aws_region`: AWS region (default `us-east-1`).
- `project_tag`: Naming/tagging prefix for all resources.
- `vpc_cidr`, `public_subnet_cidrs`, `private_subnet_cidrs`: Network layout.
- `enable_nat_gateway`, `enable_flow_logs`: Networking features.
- `create_rds` and the `db_*` inputs: Database provisioning.
- `monitoring_*` and `log_retention_days`: Observability toggles.

## Outputs
- `vpc_id`, `public_subnet_ids`, `private_subnet_ids`
- `assets_bucket`, `rds_endpoint`
- `monitoring_topic_arn`

## Security & Compliance
- **State security**: Remote state uses versioned, encrypted S3 with DynamoDB locking.
- **Network controls**: Private subnets default to NAT egress only; VPC Flow Logs are enabled by default.
- **Data protection**: S3 buckets enforce SSE and public access blocks; RDS uses generated passwords when not provided.
- **Identity**: GitHub Actions uses OIDC-ready workflow steps; avoid long-lived credentials.

## Cost Awareness
- NAT Gateways incur hourly and data processing charges—disable via `enable_nat_gateway` for sandbox use.
- RDS instances have ongoing compute/storage costs—set `create_rds = false` when not needed.
- CloudWatch logs and alarms incur minimal fees; adjust `log_retention_days` to control storage.

## CI/CD
GitHub Actions under `.github/workflows/terraform.yml` run fmt, validate, tfsec, tflint, checkov, and plan. The apply job is gated by the `production` environment for manual approval. Configure the following secrets:
- `AWS_REGION`, `TFSTATE_BUCKET`
- `AWS_ROLE_ARN_PLAN` / `AWS_ROLE_ARN_APPLY` (preferred OIDC) or legacy access keys

## Diagrams
See `docs/terraform/diagrams.md` for the architecture, VPC, and component relationships.
