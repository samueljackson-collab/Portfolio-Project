# Platform Terraform Stack

This configuration provisions a full-stack footprint for the portfolio platform using battle-tested modules already present in the repository. The root stack stitches together the VPC, ECS/Fargate application tier, and PostgreSQL database with sensible defaults for dev, staging, and production.

## Layout
- `main.tf` wires the VPC, ECS application, and database modules.
- `variables.tf` declares operator-tunable inputs for region, sizing, and tagging.
- `terraform.tfvars.example` gives a production-ready template for environment-specific values.
- `modules/` contains the reusable building blocks (VPC, ECS app, database).

## Usage
```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### Required inputs
- `project_name` and `environment` drive naming and tagging.
- `db_username` / `db_password` should come from a secret manager in real deployments.
- `container_image` is the image pushed by CI to ECR/GHCR.

### Outputs
- `vpc_id` for network integrations
- `alb_dns_name` for the front door of the service
- `db_endpoint` for application connection strings

## Notes
- NAT gateways are single-AZ in dev for cost savings and multi-AZ elsewhere.
- RDS deletion protection toggles on automatically in production.
- Autoscaling defaults target balanced CPU/memory and can be tuned via module variables.
