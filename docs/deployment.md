# Deployment Guide

This runbook covers the workflow for bootstrapping and deploying the reference infrastructure using Terraform.

## Prerequisites

- Terraform 1.6 or later
- AWS CLI configured with an IAM user or role that has administrative permissions for the target account
- Remote state backend resources (S3 bucket and DynamoDB table) created if using remote state
- Secrets configured in GitHub Actions (see the main guide for details)

## Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/aws-multi-tier-architecture.git
   cd aws-multi-tier-architecture
   ```
2. **Copy and edit variables**
   ```bash
   cp examples/terraform.tfvars.example terraform.tfvars
   $EDITOR terraform.tfvars
   ```
3. **Bootstrap Terraform**
   ```bash
   cd infrastructure/terraform
   terraform init
   ```
4. **Inspect the execution plan**
   ```bash
   terraform plan
   ```
5. **Apply the infrastructure**
   ```bash
   terraform apply
   ```
6. **Validate outputs**
   ```bash
   terraform output
   ```
7. **Destroy when finished testing**
   ```bash
   terraform destroy
   ```

## Operational Tips

- Always review the plan output carefully before applying.
- Use Terraform workspaces or distinct state files for each environment (dev/staging/prod).
- Commit infrastructure changes through pull requests so GitHub Actions can validate the plan automatically.
