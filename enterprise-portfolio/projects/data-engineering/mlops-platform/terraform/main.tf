terraform {
  required_version = ">= 1.4.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region to target"
  type        = string
  default     = "us-west-2"
}

output "module_enabled" {
  description = "Indicates that the terraform template is ready for customization."
  value       = true
}
