# Architecture

Stack: Terraform 1.6, Terragrunt, tfsec, tflint, and GitHub Actions.

Data/Control flow: Terragrunt wrappers configure backends/workspaces, apply modules to provision VPCs, AKS/EKS clusters, and shared services.

Dependencies:
- Terraform 1.6+ with provider plugins for AWS (~> 5.0) and Azure (~> 3.0).
- Terragrunt for DRY configuration and remote state management (S3/Azure Blob).
- tfsec and tflint for security and best-practice validation in CI pipeline.
- AWS credentials with permissions for VPC, EKS, IAM; Azure credentials for VNet, AKS, RBAC.
- Env/config: see README for required secrets and endpoints.
