terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version="~>5.0" }
    random = { source = "hashicorp/random", version="~>3.6" }
  }
}
module "network" {
  source             = "./modules/network"
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}
