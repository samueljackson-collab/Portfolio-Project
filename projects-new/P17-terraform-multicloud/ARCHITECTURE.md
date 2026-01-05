# Architecture

Stack: Terraform 1.6, Terragrunt, tfsec, tflint, and GitHub Actions.

Data/Control flow: Terragrunt wrappers configure backends/workspaces, apply modules to provision VPCs, AKS/EKS clusters, and shared services.

Dependencies:
- Env/config: see README for required secrets and endpoints.
