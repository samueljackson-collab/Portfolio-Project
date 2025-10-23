terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "network" {
  source = "../../modules/network"

  name              = "${var.project_name}-${var.environment}"
  vpc_cidr          = var.vpc_cidr
  public_subnets    = var.public_subnets
  private_subnets   = var.private_subnets
  database_subnets  = var.database_subnets
  enable_nat_gateways = var.enable_nat_gateways
  app_port          = var.app_port
  database_port     = var.database_port
  ssm_prefix_list_ids = var.ssm_prefix_list_ids
  tags              = local.default_tags
}

module "compute" {
  source = "../../modules/compute"

  name                       = "${var.project_name}-${var.environment}"
  environment                = var.environment
  ami_id                     = var.ami_id
  instance_type              = var.instance_type
  root_block_device          = var.root_block_device
  ssm_instance_profile       = var.ssm_instance_profile
  user_data_template         = "${path.module}/templates/user_data.sh.tpl"
  log_level                  = var.log_level
  vpc_id                     = module.network.vpc_id
  public_subnet_ids          = module.network.public_subnet_ids
  private_subnet_ids         = module.network.private_subnet_ids
  alb_security_group_id      = module.network.alb_security_group_id
  compute_security_group_id  = module.network.compute_security_group_id
  app_port                   = var.app_port
  health_check_path          = var.health_check_path
  acm_certificate_arn        = var.acm_certificate_arn
  alb_ssl_policy             = var.alb_ssl_policy
  min_size                   = var.min_size
  max_size                   = var.max_size
  desired_capacity           = var.desired_capacity
  enable_deletion_protection = true
  tags                       = local.default_tags
}

module "storage" {
  source = "../../modules/storage"

  name                        = "${var.project_name}-${var.environment}"
  environment                 = var.environment
  database_subnet_ids         = module.network.database_subnet_ids
  database_security_group_id  = module.network.database_security_group_id
  engine                      = var.database_engine
  engine_version              = var.database_engine_version
  instance_class              = var.database_instance_class
  allocated_storage           = var.database_allocated_storage
  max_allocated_storage       = var.database_max_allocated_storage
  backup_retention_period     = var.database_backup_retention
  username                    = var.database_username
  password                    = var.database_password
  kms_key_arn                 = var.kms_key_arn
  enhanced_monitoring_role_arn = var.enhanced_monitoring_role_arn
  cdn_certificate_arn         = var.cdn_certificate_arn
  cdn_price_class             = var.cdn_price_class
  tags                        = local.default_tags
}

locals {
  default_tags = merge({
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
  }, var.additional_tags)
}

resource "aws_ssm_parameter" "alb_dns" {
  name  = "/${var.project_name}/${var.environment}/alb_dns"
  type  = "String"
  value = module.compute.alb_dns_name

  tags = local.default_tags
}

resource "aws_ssm_parameter" "target_group_arn" {
  name  = "/${var.project_name}/${var.environment}/target_group_arn"
  type  = "String"
  value = module.compute.target_group_arn

  tags = local.default_tags
}

resource "aws_ssm_parameter" "rds_endpoint" {
  name  = "/${var.project_name}/${var.environment}/rds_endpoint"
  type  = "String"
  value = module.storage.rds_endpoint

  tags = local.default_tags
}

