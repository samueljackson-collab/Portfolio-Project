terraform {
  required_version = ">= 1.0"
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

data "aws_availability_zones" "available" {}

module "vpc" {
  source = "../../modules/vpc"

  name_prefix          = var.project_tag
  cidr_block           = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = slice(data.aws_availability_zones.available.names, 0, length(var.public_subnet_cidrs))
  enable_nat_gateway   = true
  tags = {
    Environment = "example"
    Project     = var.project_tag
  }
}

module "app" {
  source = "../../modules/app"

  project_tag        = var.project_tag
  vpc_id             = module.vpc.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.vpc.private_subnet_ids

  create_rds           = true
  db_name              = "portfolio_db"
  db_username          = "portfolio_admin"
  db_password          = ""
  db_allocated_storage = 20
  db_instance_class    = "db.t3.micro"
  db_engine_version    = "15.5"
  db_backup_retention  = 7
  tags = {
    Environment = "example"
    Project     = var.project_tag
  }
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_tag      = var.project_tag
  log_group_names  = [module.app.app_log_group_name]
  rds_identifier   = module.app.rds_identifier
  alarm_emails     = ["alerts@example.com"]
  enable_rds_alarm = true
  log_retention    = 14
  tags = {
    Environment = "example"
    Project     = var.project_tag
  }
}
