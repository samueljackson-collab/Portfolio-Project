terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.29"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "frontend" {
  bucket = var.frontend_bucket_name
  tags = {
    Project = "portfolio"
    ManagedBy = "terraform"
  }
}

resource "aws_ecs_cluster" "portfolio" {
  name = "portfolio-cluster"
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}
