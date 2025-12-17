/**
 * Root Terraform configuration for portfolio infrastructure
 * Provisions multi-tier architecture with networking, compute, storage, monitoring
 */
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws    = { source = "hashicorp/aws",    version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

module "network" {
  source             = "./modules/network"
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  enable_nat_gateway = var.enable_nat_gateway
  enable_vpn_gateway = var.enable_vpn_gateway
  tags               = local.common_tags
}
