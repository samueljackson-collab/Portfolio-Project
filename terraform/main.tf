provider "aws" {
  region = var.aws_region
}

locals {
  common_tags = merge({
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }, var.tags)
}

module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  enable_nat_gateway = var.enable_nat_gateway
  tags               = local.common_tags
}

module "app" {
  source = "./modules/app"

  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.vpc.vpc_id
  vpc_cidr                = var.vpc_cidr
  private_subnet_ids      = module.vpc.private_subnet_ids
  public_subnet_ids       = module.vpc.public_subnet_ids
  create_rds              = var.create_rds
  db_name                 = var.db_name
  db_username             = var.db_username
  db_password             = var.db_password
  db_allocated_storage    = var.db_allocated_storage
  db_instance_class       = var.db_instance_class
  db_engine_version       = var.db_engine_version
  allowed_cidrs           = var.allowed_cidrs
  app_bucket_force_destroy = var.app_bucket_force_destroy
  tags                   = local.common_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  project_name         = var.project_name
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  enable_flow_logs     = var.enable_flow_logs
  log_retention_days   = var.log_retention_days
  sns_subscribers      = var.alert_email_addresses
  rds_instance_arn     = module.app.rds_instance_arn
  rds_instance_id      = module.app.rds_identifier
  tags                 = local.common_tags
}
