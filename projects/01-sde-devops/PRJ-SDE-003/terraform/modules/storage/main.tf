terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Storage module placeholder: define S3 buckets for static assets, CloudFront distributions,
# and origin access controls once implementation begins.
