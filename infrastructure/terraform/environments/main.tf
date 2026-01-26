terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure remote state store with sensible defaults. Override bucket and
  # DynamoDB table names in your workspace-specific backend config when
  # bootstrapping state for the first time.
  backend "s3" {
    bucket         = "portfolio-terraform-state"
    key            = "${terraform.workspace}/infrastructure.tfstate"
    region         = "us-east-1"
    dynamodb_table = "portfolio-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.extra_tags
  )
}

module "network" {
  source      = "../modules/vpc"
  project_name = var.project_name
  environment  = var.environment

  vpc_cidr             = var.vpc_cidr
  az_count             = var.az_count
  enable_nat_gateway   = var.enable_nat_gateway
  single_nat_gateway   = var.single_nat_gateway
  enable_flow_logs     = true
  flow_logs_retention_days = 14
  tags                 = local.tags
}

module "database" {
  source        = "../modules/database"
  project_name  = var.project_name
  environment   = var.environment
  vpc_id        = module.network.vpc_id
  subnet_ids    = module.network.database_subnet_ids

  db_username   = var.db_username
  db_password   = var.db_password
  instance_class = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  multi_az             = var.db_multi_az
  backup_retention     = var.db_backup_retention
  allowed_security_group_ids = [module.app.ecs_service_security_group]

  tags = local.tags
}

module "app" {
  source      = "../modules/ecs-application"
  project_name = var.project_name
  environment  = var.environment

  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids

  container_image = var.container_image
  container_port  = var.container_port
  task_cpu        = var.task_cpu
  task_memory     = var.task_memory
  desired_count   = var.desired_count
  enable_execute_command = true

  environment_variables = [
    { name = "DATABASE_HOST", value = module.database.db_endpoint },
    { name = "OTEL_EXPORTER_OTLP_ENDPOINT", value = var.otel_exporter_endpoint },
    { name = "ENVIRONMENT", value = var.environment }
  ]

  tags = local.tags
}

output "network" {
  description = "Networking primitives for the environment"
  value = {
    vpc_id              = module.network.vpc_id
    public_subnet_ids   = module.network.public_subnet_ids
    private_subnet_ids  = module.network.private_subnet_ids
    database_subnet_ids = module.network.database_subnet_ids
  }
}

output "database" {
  description = "Database connection metadata"
  value = {
    endpoint = module.database.db_endpoint
    username = var.db_username
  }
}

output "application" {
  description = "ECS application deployment details"
  value = {
    cluster_arn      = module.app.ecs_cluster_arn
    service_name     = module.app.ecs_service_name
    load_balancer_dns = module.app.lb_dns_name
  }
}
