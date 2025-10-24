# Infrastructure-as-Code

Terraform modules and environment configurations for deploying the portfolio stack to AWS.

## Modules
- `network`: VPC, subnets, gateways, and security groups.
- `compute`: Launch template, Auto Scaling Group, and Application Load Balancer.
- `storage`: RDS PostgreSQL, S3 buckets, and CloudFront distribution.

## Usage
```bash
cd infra/environments/dev
terraform init
terraform plan
terraform apply
```

Each environment has its own `terraform.tfvars` and backend configuration. Update variable values to match account-specific requirements.
