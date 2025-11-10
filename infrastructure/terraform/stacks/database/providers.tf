/**
 * Provider configuration for the database module orchestration layer.
 * - Declares Terraform and provider versions to guarantee compatibility.
 * - Configures default tags applied to all AWS resources created by Terraform.
 * - Supports AWS IAM Role assumption for CI/CD pipelines or human operators.
 */
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.32"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge(
      {
        "Project"     = var.project_name,
        "Environment" = var.environment
      },
      var.tags
    )
  }

  # Optional assume role block for CI/CD jobs that use IAM Roles Anywhere or OIDC federation.
  dynamic "assume_role" {
    for_each = var.deployment_role_arn == "" ? [] : [var.deployment_role_arn]
    content {
      role_arn     = assume_role.value
      session_name = "terraform-${var.project_name}-${var.environment}"
    }
  }
}
