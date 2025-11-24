# Multi-region topology (AWS)

This configuration provisions paired AWS regions with mirrored networking, multi-region storage replication, and EKS control-plane placeholders designed to be reconciled by GitOps tools.

## What it creates
- Dedicated VPCs with private subnets in the primary and secondary regions.
- Cross-region S3 artifact replication using an IAM replication role.
- DynamoDB global table for configuration state shared across regions.
- EKS clusters (control plane only) ready for node-group attachment via GitOps or managed node groups.

## Usage
```bash
cd infrastructure/terraform/multi-region
terraform init
terraform plan -var="eks_role_arn=arn:aws:iam::123456789012:role/EKSControlPlane"
terraform apply -var-file=envs/prod.tfvars
```

Provide `envs/*.tfvars` for region- or environment-specific CIDR blocks and Kubernetes versions. Outputs include artifact bucket names and cluster identifiers for wiring into GitOps manifests.
