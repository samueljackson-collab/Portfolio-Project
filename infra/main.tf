terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.42"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

module "network" {
  source       = "./modules/network"
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  azs          = var.availability_zones
  tags         = local.common_tags
}

module "compute" {
  source           = "./modules/compute"
  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.network.vpc_id
  public_subnets   = module.network.public_subnet_ids
  private_subnets  = module.network.private_subnet_ids
  alb_sg_id        = module.network.alb_security_group_id
  app_sg_id        = module.network.app_security_group_id
  instance_type    = var.instance_type
  desired_capacity = var.desired_capacity
  tags             = local.common_tags
}

module "storage" {
  source                = "./modules/storage"
  project_name          = var.project_name
  environment           = var.environment
  db_subnet_ids         = module.network.db_subnet_ids
  db_security_group_id  = module.network.db_security_group_id
  db_instance_class     = var.db_instance_class
  allocated_storage     = var.db_allocated_storage
  master_username       = var.db_master_username
  master_password       = var.db_master_password
  tags                  = local.common_tags
}
