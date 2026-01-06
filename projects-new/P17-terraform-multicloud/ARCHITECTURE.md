# Architecture

Stack: Terraform 1.6, Terragrunt, tfsec, tflint, and GitHub Actions.

Data/Control flow: Terragrunt wrappers configure backends/workspaces, apply modules to provision VPCs, AKS/EKS clusters, and shared services.

Dependencies:
- Terraform 1.6+ with AWS and Azure providers configured.
- Terragrunt for DRY configuration and state management across environments.
- AWS CLI with credentials and S3/DynamoDB for remote state backend.
- Azure CLI with credentials and Blob Storage for remote state backend.
- tfsec and tflint installed for security scanning and linting in CI pipeline.
- IAM roles/policies in AWS and RBAC assignments in Azure for provisioning resources.
- Env/config: see README for required secrets and endpoints.
