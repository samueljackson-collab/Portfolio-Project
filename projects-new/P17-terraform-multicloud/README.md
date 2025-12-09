# P17 – Terraform Multi-Cloud Modules

Reusable Terraform modules for AWS and Azure with remote state and CI validation.

## Quick start
- Stack: Terraform 1.6, Terragrunt, tfsec, tflint, and GitHub Actions.
- Flow: Terragrunt wrappers configure backends/workspaces, apply modules to provision VPCs, AKS/EKS clusters, and shared services.
- Run: make lint-terraform then make plan-all
- Operate: Rotate backend credentials, lock state with DynamoDB/Blob locks, and tag all resources consistently.
