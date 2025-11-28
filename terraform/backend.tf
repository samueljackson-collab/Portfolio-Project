# Terraform Backend Configuration
# ================================
# This configures remote state storage in AWS S3 with DynamoDB locking.
#
# SETUP INSTRUCTIONS:
# ===================
# 1. Run the bootstrap script to create S3 bucket and DynamoDB table:
#    ./scripts/bootstrap_remote_state.sh <project-name> <aws-region>
#
#    Example:
#    ./scripts/bootstrap_remote_state.sh twisted-monk us-east-1
#
# 2. The script will output the values you need below.
#
# 3. Uncomment the backend block below and fill in the values.
#
# 4. Run: terraform init
#    Terraform will migrate local state to S3.
#
# SECURITY NOTES:
# ===============
# - S3 bucket has versioning enabled (state history)
# - Encryption at rest enabled (AES256)
# - DynamoDB table prevents concurrent modifications
# - Bucket is private with no public access

terraform {
  backend "s3" {
    bucket         = var.tfstate_bucket
    key            = var.tfstate_key
    region         = var.aws_region
    dynamodb_table = var.tfstate_lock_table
    encrypt        = true
  }

  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
