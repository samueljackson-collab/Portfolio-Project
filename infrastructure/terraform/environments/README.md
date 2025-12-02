# Environment Definitions

Reusable staging and production blueprints that compose the VPC, RDS database, and ECS service modules. Each environment keeps defaults that allow `terraform validate` to run while encouraging operators to override sensitive values via `terraform.tfvars` or environment variables.

## Usage

```bash
cd infrastructure/terraform/environments/staging
terraform init
terraform plan -var db_password="$(op read op://platform/postgres_password)"
```

Switch to production by changing directories. Outputs surface the ALB endpoint, ECS cluster, and database endpoints for downstream automation.
