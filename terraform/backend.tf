# Terraform Backend Configuration
# ================================
# Remote state is stored in S3 with DynamoDB table locking. Supply values
# via -backend-config flags (recommended) or by defining them in a
# terraform.tfbackend file that is not committed to source control.
# Example:
# terraform init -backend-config="bucket=my-tfstate" \
#   -backend-config="key=portfolio/terraform.tfstate" \
#   -backend-config="region=us-east-1" \
#   -backend-config="dynamodb_table=my-tf-locks"

terraform {
  required_version = ">= 1.5.0"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.48"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
