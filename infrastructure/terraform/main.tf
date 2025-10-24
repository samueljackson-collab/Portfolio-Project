terraform {
  required_version = "~> 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "network" {
  source = "./modules/vpc"

  project_name        = var.project_name
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  az_count            = var.az_count
  alb_allowed_cidrs   = var.alb_allowed_cidrs
  create_nat_gateways = var.create_nat_gateways
  tags                = var.tags
}

module "compute" {
  source = "./modules/compute"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.network.vpc_id
  subnet_ids            = module.network.private_subnet_ids
  alb_target_group_arn  = module.network.alb_target_group_arn
  alb_security_group_id = module.network.alb_security_group_id
  instance_type         = var.instance_type
  desired_capacity      = var.asg_desired_capacity
  min_size              = var.asg_min_size
  max_size              = var.asg_max_size
  ami_id                = var.ami_id
  tags                  = var.tags
}

module "database" {
  source = "./modules/database"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.network.vpc_id
  subnet_ids                 = module.network.database_subnet_ids
  db_username                = var.db_username
  db_password                = var.db_password
  instance_class             = var.db_instance_class
  allocated_storage          = var.db_allocated_storage
  max_allocated_storage      = var.db_max_allocated_storage
  engine_version             = var.db_engine_version
  multi_az                   = var.db_multi_az
  backup_retention_period    = var.db_backup_retention_period
  deletion_protection        = var.db_deletion_protection
  allowed_security_group_ids = [module.compute.instance_security_group_id]
  tags                       = var.tags
}
