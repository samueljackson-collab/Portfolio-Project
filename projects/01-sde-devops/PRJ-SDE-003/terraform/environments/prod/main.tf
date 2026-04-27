terraform {
  required_version = ">= 1.6.0"

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

module "vpc" {
  source = "../../modules/vpc"

  project_name               = var.project_name
  environment                = var.environment
  vpc_cidr                   = var.vpc_cidr
  azs_count                  = var.azs_count
  enable_nat_gateway         = var.enable_nat_gateway
  single_nat_gateway         = var.single_nat_gateway
  enable_nat_gateway_per_az  = var.enable_nat_gateway_per_az
  enable_flow_logs           = var.enable_flow_logs
  flow_logs_retention_days   = var.flow_logs_retention_days
  enable_s3_endpoint         = var.enable_s3_endpoint
  enable_dynamodb_endpoint   = var.enable_dynamodb_endpoint
  enable_ecr_endpoints       = var.enable_ecr_endpoints
  enable_ssm_endpoints       = var.enable_ssm_endpoints
  enable_dns_hostnames       = true
  enable_dns_support         = true
  common_tags                = var.common_tags
}

# Production stack composition is layered on top of this network foundation.
