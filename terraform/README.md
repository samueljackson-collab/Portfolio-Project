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

Testing & quality:
- terraform fmt -recursive
- terraform validate
- tflint
- checkov (static security scan)
- terratest (Go) for integration tests

Notes:
- The bootstrap script creates S3 and DynamoDB for Terraform remote state. Run it once with an admin account.
- The provided main.tf is an example. Replace/add modules for VPC, EKS, RDS, etc. per your architecture.
