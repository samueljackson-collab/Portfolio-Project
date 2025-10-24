terraform {
  required_version = ">= 1.5"
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
  source              = "./modules/network"
  vpc_cidr            = var.vpc_cidr
  azs                 = var.azs
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  data_subnet_cidrs   = var.data_subnet_cidrs
  project             = var.project
  environment         = var.environment
}

module "compute" {
  source            = "./modules/compute"
  project           = var.project
  environment       = var.environment
  subnet_ids        = module.network.private_subnet_ids
  alb_subnet_ids    = module.network.public_subnet_ids
  vpc_id            = module.network.vpc_id
  instance_type     = var.instance_type
  desired_capacity  = var.desired_capacity
  max_size          = var.max_size
  min_size          = var.min_size
  alb_security_group_id    = module.network.alb_security_group_id
  backend_security_group_id = module.network.backend_security_group_id
}

module "storage" {
  source              = "./modules/storage"
  project             = var.project
  environment         = var.environment
  data_subnet_ids     = module.network.data_subnet_ids
  vpc_id              = module.network.vpc_id
  db_username         = var.db_username
  db_password         = var.db_password
  enable_multi_az     = var.enable_multi_az
  frontend_bucket_acl = var.frontend_bucket_acl
  database_security_group_id = module.network.database_security_group_id
}
