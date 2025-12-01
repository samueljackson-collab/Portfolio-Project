locals {
  base_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags,
  )
}

module "primary_vpc" {
  source = "../modules/vpc"

  providers = {
    aws = aws
  }

  project_name          = var.project_name
  environment           = var.environment
  vpc_cidr              = "10.10.0.0/16"
  az_count              = 2
  enable_nat_gateway    = true
  single_nat_gateway    = true
  enable_dns_hostnames  = true
  enable_dns_support    = true
  map_public_ip_on_launch = false
  tags                  = local.base_tags
}

module "secondary_vpc" {
  source = "../modules/vpc"

  providers = {
    aws = aws.secondary
  }

  project_name          = "${var.project_name}-dr"
  environment           = var.environment
  vpc_cidr              = "10.20.0.0/16"
  az_count              = 2
  enable_nat_gateway    = true
  single_nat_gateway    = true
  enable_dns_hostnames  = true
  enable_dns_support    = true
  map_public_ip_on_launch = false
  tags                  = local.base_tags
}

module "primary_app" {
  source = "../modules/ecs-application"

  providers = {
    aws = aws
  }

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.primary_vpc.vpc_id
  public_subnet_ids  = module.primary_vpc.public_subnet_ids
  private_subnet_ids = module.primary_vpc.private_subnet_ids
  container_image    = var.container_image
  container_port     = 8000
  health_check_path  = "/health"
  environment_variables = [
    { name = "REGION", value = var.primary_region },
    { name = "APP_ROLE", value = "primary" }
  ]
  tags = local.base_tags
}

module "secondary_app" {
  source = "../modules/ecs-application"

  providers = {
    aws = aws.secondary
  }

  project_name       = "${var.project_name}-dr"
  environment        = var.environment
  vpc_id             = module.secondary_vpc.vpc_id
  public_subnet_ids  = module.secondary_vpc.public_subnet_ids
  private_subnet_ids = module.secondary_vpc.private_subnet_ids
  container_image    = var.container_image
  container_port     = 8000
  health_check_path  = "/health"
  environment_variables = [
    { name = "REGION", value = var.secondary_region },
    { name = "APP_ROLE", value = "secondary" }
  ]
  tags = local.base_tags
}
