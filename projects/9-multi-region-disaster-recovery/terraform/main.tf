terraform {
  required_version = ">= 1.5.0"
  backend "s3" {
    bucket = "portfolio-tf-state"
    key    = "project-9/terraform.tfstate"
    region = "us-east-1"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  alias  = "primary"
  region = var.primary_region
}

provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
}

module "network_primary" {
  source  = "terraform-aws-modules/vpc/aws"
  providers = { aws = aws.primary }
  name     = "portfolio-primary"
  cidr     = var.primary_vpc_cidr
  azs      = var.primary_azs
  private_subnets = var.primary_private_subnets
  public_subnets  = var.primary_public_subnets
  enable_nat_gateway = true
}

module "network_secondary" {
  source  = "terraform-aws-modules/vpc/aws"
  providers = { aws = aws.secondary }
  name     = "portfolio-secondary"
  cidr     = var.secondary_vpc_cidr
  azs      = var.secondary_azs
  private_subnets = var.secondary_private_subnets
  public_subnets  = var.secondary_public_subnets
  enable_nat_gateway = true
}

module "aurora" {
  source = "terraform-aws-modules/rds-aurora/aws"
  providers = {
    aws          = aws.primary
    aws.secondary = aws.secondary
  }
  name                        = "portfolio-global"
  engine                      = "aurora-mysql"
  engine_mode                 = "global"
  master_username             = var.db_username
  master_password             = var.db_password
  database_name               = "portfolio"
  instances                   = 2
  availability_zones          = var.primary_azs
  replica_count               = 1
  replica_availability_zones  = var.secondary_azs
  vpc_security_group_ids      = [module.network_primary.default_security_group_id]
  db_subnet_group_name        = module.network_primary.database_subnet_group
}

resource "aws_s3_bucket" "replicated" {
  provider = aws.primary
  bucket   = var.replication_bucket_name
  versioning {
    enabled = true
  }
  replication_configuration {
    role = var.replication_role_arn
    rules {
      id       = "replicate"
      status   = "Enabled"
      priority = 1
      destination {
        bucket        = var.replication_destination_bucket
        storage_class = "STANDARD"
      }
    }
  }
}

resource "aws_route53_health_check" "primary" {
  provider = aws.primary
  fqdn     = var.health_check_fqdn
  port     = 443
  type     = "HTTPS"
  resource_path = "/health"
  failure_threshold = 3
  request_interval  = 30
}

resource "aws_route53_record" "failover" {
  zone_id = var.hosted_zone_id
  name    = var.application_domain
  type    = "A"

  set_identifier  = "primary"
  failover_routing_policy {
    type = "PRIMARY"
  }
  alias {
    name                   = var.primary_alb_dns
    zone_id                = var.primary_alb_zone_id
    evaluate_target_health = true
  }
  health_check_id = aws_route53_health_check.primary.id
}

resource "aws_route53_record" "failover_secondary" {
  zone_id = var.hosted_zone_id
  name    = var.application_domain
  type    = "A"

  set_identifier  = "secondary"
  failover_routing_policy {
    type = "SECONDARY"
  }
  alias {
    name                   = var.secondary_alb_dns
    zone_id                = var.secondary_alb_zone_id
    evaluate_target_health = true
  }
}
