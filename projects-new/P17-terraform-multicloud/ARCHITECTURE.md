# Architecture

Stack: Terraform 1.6, Terragrunt, tfsec, tflint, and GitHub Actions.

Data/Control flow: Terragrunt wrappers configure backends/workspaces, apply modules to provision VPCs, AKS/EKS clusters, and shared services.

Dependencies:
- Terraform 1.6+ CLI with AWS and Azure provider plugins.
- AWS account with IAM permissions for VPC, EKS, and S3/DynamoDB for remote state.
- Azure subscription with RBAC permissions for VNet, AKS, and Blob Storage for remote state.
- Backend storage: S3 bucket + DynamoDB table (AWS), Storage Account + Blob Container (Azure).
- Env/config: see README for required secrets and endpoints.
