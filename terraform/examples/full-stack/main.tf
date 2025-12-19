terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.48"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  base_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform-example"
  }
}

module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  enable_nat_gateway = true
  tags               = local.base_tags
}

module "app" {
  source = "../../modules/app"

  project_name             = var.project_name
  environment              = var.environment
  vpc_id                   = module.vpc.vpc_id
  vpc_cidr                 = var.vpc_cidr
  public_subnet_ids        = module.vpc.public_subnet_ids
  private_subnet_ids       = module.vpc.private_subnet_ids
  create_rds               = true
  db_name                  = "example_db"
  db_username              = "example_admin"
  db_allocated_storage     = 20
  db_instance_class        = "db.t3.micro"
  db_engine_version        = "15.5"
  allowed_cidrs            = [var.vpc_cidr]
  app_bucket_force_destroy = false
  tags                    = local.base_tags
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  enable_flow_logs   = true
  log_retention_days = 30
  sns_subscribers    = []
  rds_instance_arn   = module.app.rds_instance_arn
  rds_instance_id    = module.app.rds_identifier
  tags               = local.base_tags
}
