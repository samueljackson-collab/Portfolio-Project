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

# Uncomment and configure after running bootstrap script:
#
# terraform {
#   backend "s3" {
#     bucket         = "twisted-monk-tfstate-XXXXX"  # From bootstrap output
#     # Example using variables when leveraging partial configuration overrides:
#     # bucket         = var.terraform_backend_bucket
#     # key            = var.terraform_backend_key
#     # dynamodb_table = var.terraform_backend_dynamodb_table
#     key            = "twisted-monk/terraform.tfstate"
#     region         = "us-east-1"                    # Your AWS region
#     dynamodb_table = "twisted-monk-tfstate-lock"   # From bootstrap output
#     encrypt        = true
#   }
# }

# Local backend (default until S3 backend is configured)
terraform {
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
