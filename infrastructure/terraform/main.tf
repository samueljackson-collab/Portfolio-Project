terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.32"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.26"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

provider "kubernetes" {
  host                   = aws_eks_cluster.portfolio.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.portfolio.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.portfolio.token
}

module "tags" {
  source = "./modules/tags"

  environment = var.environment
  service     = "portfolio-api"
}

locals {
  name_prefix = "portfolio-${var.environment}"
  common_tags = merge(module.tags.common, {
    "terraform" = "true"
  })
}
