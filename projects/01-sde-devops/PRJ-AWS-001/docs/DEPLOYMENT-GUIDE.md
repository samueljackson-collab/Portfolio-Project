# Deployment Guide

## Prerequisites
- Terraform >= 1.5
- AWS CLI v2 configured with credentials for each environment
- Optional: Infracost, tfsec, Terratest tooling

## Steps
1. `cd terraform/environments/<env>`
2. Create/verify backend S3 bucket and DynamoDB lock table specified in `backend.tf`.
3. Update `terraform.tfvars` with environment secrets (AMI, DB password) or load them via TF_VAR_* environment variables.
4. Run `../../scripts/deploy.sh <env>` to initialize, validate, plan, and apply.
5. Store generated plan files and cost reports in artifact storage for audit.

## Post-Deployment Validation
- Confirm ALB DNS responds with HTTP 200.
- Validate EC2 instances registered and healthy in the target group.
- Test DB connectivity from a bastion host using security group rules.
- Inspect CloudWatch dashboard for metric ingestion.

## CI/CD Recommendations
- Use GitHub Actions or Jenkins to execute `terraform fmt`, `terraform validate`, `terraform plan`, and tfsec on each PR.
- Require manual approval before running `terraform apply` in prod.
