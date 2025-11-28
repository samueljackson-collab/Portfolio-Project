terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags,
  )
}

module "network" {
  source = "./modules/vpc"

  project_name            = var.project_name
  environment             = var.environment
  vpc_cidr                = var.vpc_cidr
  az_count                = var.az_count
  enable_dns_hostnames    = true
  enable_dns_support      = true
  enable_nat_gateway      = true
  single_nat_gateway      = var.environment == "dev"
  enable_flow_logs        = true
  flow_logs_retention_days = 14
  enable_s3_endpoint      = true
  tags                    = local.common_tags
}

module "application" {
  source = "./modules/ecs-application"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.network.vpc_id
  public_subnet_ids          = module.network.public_subnet_ids
  private_subnet_ids         = module.network.private_subnet_ids
  container_image            = var.container_image
  container_port             = 8080
  desired_count              = var.environment == "production" ? 3 : 1
  task_cpu                   = "512"
  task_memory                = "1024"
  assign_public_ip           = false
  health_check_path          = "/health"
  enable_container_insights  = true
  log_retention_days         = 30
  database_security_group_id = ""
  tags                       = local.common_tags
}

module "database" {
  source = "./modules/database"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.network.vpc_id
  db_username                = var.db_username
  db_password                = var.db_password
  subnet_ids                 = module.network.database_subnet_ids
  allowed_security_group_ids = [module.application.ecs_tasks_security_group_id]
  instance_class             = var.db_instance_class
  allocated_storage          = var.db_allocated_storage
  max_allocated_storage      = var.db_max_allocated_storage
  engine_version             = var.db_engine_version
  multi_az                   = var.environment != "dev"
  backup_retention_period    = var.db_backup_retention
  deletion_protection        = var.environment == "production"
  skip_final_snapshot        = var.environment == "dev"
  apply_immediately          = var.environment != "production"
  tags                       = local.common_tags
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = module.network.vpc_id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.application.alb_dns_name
}

output "db_endpoint" {
  description = "Database endpoint hostname"
  value       = module.database.db_endpoint
}
