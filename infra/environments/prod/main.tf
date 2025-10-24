# ============================================================================
# File: infra/environments/prod/main.tf
# Purpose: Root Terraform configuration for production environment
# ============================================================================

terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  
  backend "s3" {
    bucket         = "portfolio-terraform-state-prod"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "portfolio-terraform-locks-prod"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.owner
      CostCenter  = "engineering"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Generate secure database password
resource "random_password" "db_password" {
  length  = 32
  special = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Network Module
module "network" {
  source = "../../modules/network"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  single_nat_gateway = false # One NAT per AZ for HA
  
  tags = local.common_tags
}

# Compute Module
module "compute" {
  source = "../../modules/compute"
  
  project_name = var.project_name
  environment  = var.environment
  
  vpc_id             = module.network.vpc_id
  public_subnet_ids  = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids
  
  alb_security_group_id = module.network.alb_security_group_id
  app_security_group_id = module.network.app_security_group_id
  
  instance_type    = var.instance_type
  ami_id           = var.ami_id
  key_name         = var.key_name
  
  min_size         = var.asg_min_size
  max_size         = var.asg_max_size
  desired_capacity = var.asg_desired_capacity
  
  health_check_path     = "/health"
  health_check_interval = 30
  health_check_timeout  = 5
  healthy_threshold     = 2
  unhealthy_threshold   = 3
  
  enable_deletion_protection = var.environment == "prod"
  
  user_data = templatefile("${path.module}/user_data.sh", {
    environment   = var.environment
    db_endpoint   = module.storage.database_endpoint
    db_name       = var.db_name
    aws_region    = var.aws_region
    ecr_repo      = var.ecr_repository
    secret_arn    = module.storage.db_secret_arn
  })
  
  tags = local.common_tags
}

# Storage Module
module "storage" {
  source = "../../modules/storage"
  
  project_name = var.project_name
  environment  = var.environment
  
  vpc_id              = module.network.vpc_id
  database_subnet_ids = module.network.database_subnet_ids
  db_security_group_id = module.network.database_security_group_id
  
  db_instance_class   = var.db_instance_class
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = random_password.db_password.result
  db_allocated_storage = var.db_allocated_storage
  db_backup_retention = var.db_backup_retention
  multi_az            = var.multi_az
  
  create_read_replica = var.environment == "prod"
  
  enable_s3_versioning = true
  enable_cloudfront    = var.enable_cloudfront
  
  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"
  
  project_name = var.project_name
  environment  = var.environment
  
  alb_arn                = module.compute.alb_arn
  target_group_arn       = module.compute.target_group_arn
  asg_name               = module.compute.asg_name
  db_instance_identifier = module.storage.database_identifier
  
  alert_email = var.alert_email
  
  tags = local.common_tags
}

# Local values
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
