##############################################################################
# Example: Production PostgreSQL RDS
#
# This example provisions a production-ready PostgreSQL 15.4 instance inside
# an existing VPC.  Adjust the data sources or hard-code IDs as needed for
# your environment.
##############################################################################

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0, < 6.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

##############################################################################
# Data sources – look up existing network resources
##############################################################################

data "aws_vpc" "selected" {
  id = var.vpc_id
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  tags = {
    Tier = "private"
  }
}

##############################################################################
# RDS Module
##############################################################################

module "rds" {
  source = "../../modules/rds"

  identifier     = "myapp-prod-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.small"

  allocated_storage     = 50
  max_allocated_storage = 500

  db_name  = "myappdb"
  username = "dbadmin"

  vpc_id                 = var.vpc_id
  subnet_ids             = var.subnet_ids
  app_security_group_ids = var.app_security_group_ids

  multi_az                = true
  backup_retention_period = 14
  backup_window           = "02:00-03:00"
  maintenance_window      = "sun:03:00-sun:04:00"

  deletion_protection = true
  skip_final_snapshot = false

  tags = {
    Environment = "production"
    Project     = "myapp"
    ManagedBy   = "terraform"
    Owner       = "platform-team"
    CostCenter  = "eng-001"
  }
}

##############################################################################
# Outputs
##############################################################################

output "db_endpoint" {
  description = "PostgreSQL connection endpoint."
  value       = module.rds.db_instance_endpoint
}

output "db_port" {
  description = "PostgreSQL port."
  value       = module.rds.db_instance_port
}

output "db_instance_id" {
  description = "RDS instance identifier."
  value       = module.rds.db_instance_id
}

output "db_instance_arn" {
  description = "ARN of the RDS instance."
  value       = module.rds.db_instance_arn
}

output "secret_arn" {
  description = "Secrets Manager ARN containing DB credentials."
  value       = module.rds.secret_arn
  sensitive   = true
}

output "security_group_id" {
  description = "Security group ID attached to the RDS instance."
  value       = module.rds.security_group_id
}
