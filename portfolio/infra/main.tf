provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "portfolio"
      Environment = var.environment
      Owner       = var.owner
    }
  }
}

module "network" {
  source              = "./modules/network"
  vpc_cidr_block      = var.vpc_cidr_block
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

resource "aws_ecr_repository" "backend" {
  name = "portfolio-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "frontend" {
  name = "portfolio-frontend"
  image_tag_mutability = "MUTABLE"
}
