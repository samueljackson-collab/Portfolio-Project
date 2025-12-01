provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {}

locals {
  common_tags = {
    Project     = var.project_tag
    Environment = terraform.workspace
    ManagedBy   = "terraform"
  }
}

module "vpc" {
  source = "./modules/vpc"

  name_prefix          = var.project_tag
  cidr_block           = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = var.enable_nat_gateway
  enable_flow_logs     = var.enable_flow_logs
  availability_zones   = slice(data.aws_availability_zones.available.names, 0, length(var.public_subnet_cidrs))
  tags                 = local.common_tags
}

module "app" {
  source = "./modules/app"

  project_tag        = var.project_tag
  vpc_id             = module.vpc.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.vpc.private_subnet_ids

  create_rds           = var.create_rds
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
  db_allocated_storage = var.db_allocated_storage
  db_instance_class    = var.db_instance_class
  db_engine_version    = var.db_engine_version
  db_backup_retention  = var.db_backup_retention
  assets_bucket_name   = var.assets_bucket_name
  tags                 = local.common_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  project_tag      = var.project_tag
  log_group_names  = compact([module.vpc.flow_log_group_name, module.app.app_log_group_name])
  rds_identifier   = module.app.rds_identifier
  alarm_emails     = var.monitoring_alarm_emails
  enable_rds_alarm = var.monitoring_enable_rds_alarm
  log_retention    = var.log_retention_days
  tags             = local.common_tags
}
