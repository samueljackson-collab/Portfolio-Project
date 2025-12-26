# AWS RDS Module

Creates a managed PostgreSQL or MySQL database with Multi-AZ, read replicas, parameter groups, backups, and Secrets Manager integration.

## Usage

```hcl
module "rds" {
  source = "../modules/aws/rds"

  project_name          = "portfolio"
  environment           = "prod"
  vpc_id                = module.vpc.vpc_id
  db_subnet_ids         = module.vpc.private_subnet_ids
  allowed_cidr_blocks   = ["10.20.0.0/16"]
  engine                = "postgres"
  engine_version        = "15.5"
  parameter_group_family = "postgres15"
  multi_az              = true
  read_replica_count    = 1
  tags = {
    Owner = "platform-team"
  }
}
```

## Outputs
- `db_instance_id`
- `db_endpoint`
- `replica_endpoints`
- `security_group_id`
- `secret_arn`
- `subnet_group_name`
