terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Compute module placeholder: define launch templates, autoscaling groups, target groups,
# and ALB wiring using inputs declared in variables.tf. This file intentionally focuses on
# the Terraform scaffolding so it can be iterated independently of the VPC module.
