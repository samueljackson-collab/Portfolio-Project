# GitHub Repository Setup Guide

This guide describes the minimal steps to get started with this repository locally and to configure CI/Deploy.

Prerequisites
- Git
- Terraform 1.6.x (or compatible)
- AWS CLI configured (if you will deploy)

Quickstart
1. Clone the repository
   git clone https://github.com/samueljackson-collab/Portfolio-Project.git
   cd Portfolio-Project

2. Branching
   Create a feature branch for changes:
   git checkout -b feat/your-change

3. Local Terraform variables
   Copy the example tfvars and edit locally (do NOT commit secrets):
   cp examples/terraform.tfvars.example terraform.tfvars
   $EDITOR terraform.tfvars

4. Validate infrastructure locally
   cd infrastructure/terraform
   terraform init -backend=false
   terraform fmt -check -recursive
   terraform validate

5. Running CI checks
   - CI runs terraform fmt, init, validate and tflint. Ensure those pass locally before opening a PR.

6. Secrets and GitHub Actions
   - Define necessary repository secrets in Settings > Secrets and variables > Actions (e.g. AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION).
   - For production-grade usage prefer OIDC role assumption rather than long-lived access keys.

7. Opening a Pull Request
   Push your branch and open a PR targeting main. Provide a description of your change, relevant plan output for infra changes, and any cost/security implications.

Notes
- Never commit real passwords or secrets. Use GitHub Actions secrets or AWS Secrets Manager for runtime secrets.