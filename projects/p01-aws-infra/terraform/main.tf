terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Configure with:
    # terraform init -backend-config="bucket=my-terraform-state-bucket" \
    #                -backend-config="key=p01-aws-infra/terraform.tfstate" \
    #                -backend-config="region=us-east-1" \
    #                -backend-config="dynamodb_table=terraform-state-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "P01-AWS-Infrastructure"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Repository  = "Portfolio-Project"
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  environment        = var.environment
  vpc_cidr          = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  environment = var.environment
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  environment            = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  db_name               = var.db_name
  db_instance_class     = var.db_instance_class
  db_master_username    = var.db_master_username
  db_master_password    = var.db_master_password
  multi_az              = var.multi_az
  backup_retention_period = var.backup_retention_period
  allowed_cidr_blocks   = [var.vpc_cidr]
}
