# Terraform Infrastructure

Defines AWS infrastructure for the portfolio stack with reusable modules.

## Modules
- `network` – VPC, subnets, routing, security groups.
- `compute` – Auto Scaling groups and load balancers for backend services.
- `storage` – RDS PostgreSQL, S3 buckets, CloudFront distribution.

## Usage

```bash
cd environments/dev
tfenv use 1.6.0 # optional
terraform init
terraform apply
```

Set backend configuration in `backend.tf` before running `init`.

