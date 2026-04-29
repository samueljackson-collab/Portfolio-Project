terraform {
  required_version = ">= 1.4.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.default_tags
  }
}

module "network" {
  source     = "./modules/network"
  name       = "${var.environment}-core"
  cidr_block = var.network_cidr
  tags       = var.default_tags
}

module "security" {
  source     = "./modules/security"
  frameworks = var.security_frameworks
}

module "monitoring" {
  source         = "./modules/monitoring"
  enable_metrics = true
  enable_logs    = true
  enable_traces  = var.enable_tracing
}

module "eks" {
  source             = "./modules/eks"
  name               = "${var.environment}-gitops"
  kubernetes_version = var.kubernetes_version
  node_pools         = var.node_pools
}
