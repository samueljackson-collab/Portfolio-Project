# Terraform Remote State Backend Configuration
# =============================================
# This file configures S3 backend for remote state storage with DynamoDB locking.
#
# Prerequisites:
# 1. S3 bucket for state storage
# 2. DynamoDB table for state locking
# 3. IAM permissions for Terraform to access S3 and DynamoDB
#
# To create the backend resources, run:
#   ./scripts/bootstrap-backend.sh
#
# After backend is created, uncomment the backend block and run:
#   terraform init -migrate-state

terraform {
  # Backend configuration for remote state storage
  # Uncomment after running bootstrap-backend.sh script

  # backend "s3" {
  #   # S3 bucket for state storage (must be unique globally)
  #   bucket = "terraform-state-prj-sde-001"
  #
  #   # Path to state file within bucket
  #   key = "full-stack-app/terraform.tfstate"
  #
  #   # AWS region for S3 bucket
  #   region = "us-east-1"
  #
  #   # DynamoDB table for state locking (prevents concurrent modifications)
  #   dynamodb_table = "terraform-state-lock"
  #
  #   # Enable server-side encryption for state file
  #   encrypt = true
  #
  #   # S3 bucket versioning enabled (via bootstrap script)
  #   # Allows state file recovery if corrupted
  # }
}

# Backend Configuration Notes:
# ============================
#
# State File Security:
# - State files contain sensitive data (passwords, connection strings)
# - S3 encryption at rest is enabled (AES-256)
# - Bucket policy enforces SSL/TLS for all requests
# - Versioning enabled for state file recovery
# - MFA delete protection recommended for production
#
# DynamoDB Locking:
# - Prevents concurrent terraform apply operations
# - Lock timeout: 20 minutes (default)
# - Lock is released automatically on success or failure
# - Use `terraform force-unlock <lock-id>` only in emergencies
#
# Multi-Environment Strategy:
# - Option 1: Separate state files per environment (current approach)
#   - dev:   key = "dev/terraform.tfstate"
#   - stage: key = "stage/terraform.tfstate"
#   - prod:  key = "prod/terraform.tfstate"
#
# - Option 2: Separate S3 buckets per environment
#   - dev:   bucket = "terraform-state-dev"
#   - stage: bucket = "terraform-state-stage"
#   - prod:  bucket = "terraform-state-prod"
#
# Backend Migration:
# ------------------
# If migrating from local to remote state:
#   1. Run bootstrap script to create backend resources
#   2. Uncomment backend block above
#   3. Run: terraform init -migrate-state
#   4. Confirm migration when prompted
#   5. Verify: terraform state list
#   6. Delete local terraform.tfstate file (after backup)
#
# State File Backup:
# ------------------
# S3 bucket versioning maintains historical state files.
# To restore a previous version:
#   1. List versions: aws s3api list-object-versions --bucket <bucket> --prefix <key>
#   2. Restore version: aws s3api get-object --bucket <bucket> --key <key> --version-id <id> terraform.tfstate.backup
#   3. Move backup to terraform.tfstate
#   4. Run: terraform plan (verify state is correct)
#
# Disaster Recovery:
# ------------------
# 1. S3 bucket has cross-region replication enabled (via bootstrap)
# 2. DynamoDB table has point-in-time recovery enabled
# 3. State file backups are kept for 90 days (lifecycle policy)
# 4. Recovery procedure documented in DISASTER_RECOVERY.md
#
# Cost Optimization:
# ------------------
# - S3 Standard storage: ~$0.023/GB/month
# - DynamoDB on-demand pricing: $1.25 per million requests
# - Expected monthly cost: <$5 for typical usage
# - Use S3 Intelligent-Tiering for large state files (>1MB)
