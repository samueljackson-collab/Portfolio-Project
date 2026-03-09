terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

locals {
  common_tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Project     = var.project_name
    }
  )
}

module "networking" {
  source = "../../modules/networking"

  project_name       = var.project_name
  environment        = var.environment
  aws_region         = var.aws_region
  availability_zones = var.availability_zones
  vpc_cidr           = var.vpc_cidr

  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = var.single_nat_gateway
  enable_vpc_flow_logs   = var.enable_vpc_flow_logs
  flow_logs_retention_days = var.flow_logs_retention_days
  enable_s3_endpoint     = true
  enable_dynamodb_endpoint = true
  db_port                = var.db_port

  cost_center = var.cost_center
  common_tags = local.common_tags
}

module "security" {
  source = "../../modules/security"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.networking.vpc_id

  alb_ingress_cidrs = var.alb_ingress_cidrs
  bastion_cidrs     = var.bastion_cidrs
  app_port          = var.app_port
  db_port           = var.db_port

  common_tags = local.common_tags
}

module "storage" {
  source = "../../modules/storage"

  project_name      = var.project_name
  environment       = var.environment
  bucket_name       = var.artifact_bucket_name
  force_destroy     = var.force_destroy_buckets
  enable_versioning = true
  kms_key_id        = var.kms_key_id
  common_tags       = local.common_tags
}

module "compute" {
  source = "../../modules/compute"

  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.networking.vpc_id
  public_subnet_ids      = module.networking.public_subnet_ids
  private_app_subnet_ids = module.networking.private_app_subnet_ids
  alb_security_group_id  = module.security.alb_security_group_id
  app_security_group_id  = module.security.app_security_group_id
  common_tags            = local.common_tags

  ami_id                 = var.ami_id
  instance_type          = var.instance_type
  ssh_key_name           = var.ssh_key_name
  iam_instance_profile   = var.iam_instance_profile
  user_data_base64       = var.user_data_base64
  desired_capacity       = var.desired_capacity
  min_size               = var.min_size
  max_size               = var.max_size
  app_port               = var.app_port
  health_check_path      = var.health_check_path
  target_cpu_utilization = var.target_cpu_utilization
}

module "database" {
  source = "../../modules/database"

  project_name           = var.project_name
  environment            = var.environment
  private_db_subnet_ids  = module.networking.private_db_subnet_ids
  db_security_group_ids  = [module.security.db_security_group_id]
  db_name                = var.db_name
  db_engine              = var.db_engine
  db_engine_version      = var.db_engine_version
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  max_allocated_storage  = var.db_max_allocated_storage
  backup_retention_days  = var.db_backup_retention_days
  deletion_protection    = var.db_deletion_protection
  db_username            = var.db_username
  db_password            = var.db_password
  multi_az               = var.db_multi_az
  kms_key_id             = var.kms_key_id
  performance_insights_enabled = var.db_performance_insights
  common_tags            = local.common_tags
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_name         = var.project_name
  environment          = var.environment
  asg_name             = module.compute.asg_name
  alb_metric_name      = module.compute.alb_arn_suffix
  aws_region           = var.aws_region
  alarm_sns_topic_arn  = var.alarm_sns_topic_arn
  enable_dashboard     = true
  common_tags          = local.common_tags
}
