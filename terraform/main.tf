terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  environment = coalesce(var.environment, terraform.workspace)
  common_tags = {
    Project     = var.project_tag
    Owner       = "samueljackson-collab"
    Environment = local.environment
  }
}

module "vpc" {
  source = "./modules/vpc"

  project_tag         = var.project_tag
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway  = var.enable_nat_gateway
  tags                = local.common_tags
}

module "app" {
  source = "./modules/app"

  project_tag        = var.project_tag
  environment        = local.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  vpc_cidr           = var.vpc_cidr

  asset_bucket_prefix   = var.asset_bucket_prefix
  create_rds            = var.create_rds
  db_name               = var.db_name
  db_username           = var.db_username
  db_password           = var.db_password
  db_allocated_storage  = var.db_allocated_storage
  db_instance_class     = var.db_instance_class
  db_engine_version     = var.db_engine_version
  skip_final_snapshot   = var.skip_final_snapshot
  enable_eks            = var.enable_eks
  eks_cluster_name      = var.eks_cluster_name
  eks_version           = var.eks_version

  tags = local.common_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  project_tag = var.project_tag
  environment = local.environment
  vpc_id      = module.vpc.vpc_id

  enable_flow_logs           = var.enable_flow_logs
  flow_log_retention_days    = var.flow_log_retention_days
  vpc_flow_log_traffic_type  = var.vpc_flow_log_traffic_type
  enable_rds_alarms          = var.enable_rds_alarms && var.create_rds
  rds_identifier             = module.app.rds_identifier
  alarm_email                = var.alarm_email
  rds_cpu_threshold          = var.rds_cpu_threshold
  tags                       = local.common_tags
}
