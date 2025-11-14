terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket         = var.tf_backend_bucket
    key            = "portfolio/terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = var.tf_backend_lock_table
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.34.0"
    }
  }
}
