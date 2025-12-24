terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_ssm_parameter" "solution_flag" {
  name  = "/solutions/${var.project_name}/enabled"
  type  = "String"
  value = "true"

  tags = {
    Project = var.project_name
    Purpose = "scaffold"
  }
}
