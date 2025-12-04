locals {
  common_tags = merge(
    {
      Project     = "p01-aws-infra"
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags
  )
}

module "state" {
  source               = "./modules/state"
  create               = var.bootstrap_state
  bucket_name          = var.state_bucket
  dynamodb_table_name  = var.state_lock_table
  versioning_enabled   = true
  force_destroy_bucket = false
  tags                 = local.common_tags
}

module "network" {
  source              = "./modules/network"
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  public_subnet_cidrs = var.public_subnets
  private_subnet_cidrs = var.private_subnets
  enable_nat_gateway  = var.enable_nat_gateway
  tags                = local.common_tags
}
