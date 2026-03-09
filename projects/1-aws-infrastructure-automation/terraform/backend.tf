###############################################################################
# Terraform Backend Configuration
#
# This file configures the S3 backend for storing Terraform state with
# DynamoDB for state locking. The actual values are provided via backend.hcl
# or through command-line arguments.
#
# Usage:
#   terraform init -backend-config=backend.hcl
#   terraform init -backend-config="bucket=my-bucket" -backend-config="key=my/key"
#
# Required AWS Resources (create before first use):
#   1. S3 bucket for state storage
#   2. DynamoDB table for state locking
#
# See: scripts/bootstrap-backend.sh for automated setup
###############################################################################

terraform {
  # S3 backend with DynamoDB state locking
  # Configuration values are provided via backend.hcl or CLI arguments
  backend "s3" {
    # These values can be overridden via backend.hcl or -backend-config
    # bucket         = "portfolio-tf-state"
    # key            = "project-1/terraform.tfstate"
    # region         = "us-west-2"
    # dynamodb_table = "portfolio-tf-locks"
    # encrypt        = true
  }
}

###############################################################################
# Backend Bootstrap Resources
#
# Uncomment and apply separately to create the backend infrastructure.
# After creation, migrate the state to S3 using: terraform init -migrate-state
###############################################################################

# variable "backend_bucket_name" {
#   description = "Name of the S3 bucket for Terraform state"
#   type        = string
#   default     = "portfolio-tf-state"
# }
#
# variable "backend_dynamodb_table" {
#   description = "Name of the DynamoDB table for state locking"
#   type        = string
#   default     = "portfolio-tf-locks"
# }
#
# variable "backend_region" {
#   description = "AWS region for backend resources"
#   type        = string
#   default     = "us-west-2"
# }
#
# # S3 Bucket for Terraform State
# resource "aws_s3_bucket" "terraform_state" {
#   bucket = var.backend_bucket_name
#
#   lifecycle {
#     prevent_destroy = true
#   }
#
#   tags = {
#     Name        = "Terraform State"
#     Project     = "portfolio"
#     ManagedBy   = "terraform"
#   }
# }
#
# resource "aws_s3_bucket_versioning" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
#   versioning_configuration {
#     status = "Enabled"
#   }
# }
#
# resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"
#     }
#   }
# }
#
# resource "aws_s3_bucket_public_access_block" "terraform_state" {
#   bucket                  = aws_s3_bucket.terraform_state.id
#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }
#
# # DynamoDB Table for State Locking
# resource "aws_dynamodb_table" "terraform_locks" {
#   name         = var.backend_dynamodb_table
#   billing_mode = "PAY_PER_REQUEST"
#   hash_key     = "LockID"
#
#   attribute {
#     name = "LockID"
#     type = "S"
#   }
#
#   tags = {
#     Name        = "Terraform State Locks"
#     Project     = "portfolio"
#     ManagedBy   = "terraform"
#   }
# }
