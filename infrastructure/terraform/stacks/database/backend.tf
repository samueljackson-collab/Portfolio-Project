/**
 * Remote backend configuration instructions.
 * Update the placeholders before first `terraform init` or provide a backend.hcl file.
 */
terraform {
  backend "s3" {
    # S3 bucket storing the remote state file. Enable versioning and server-side encryption.
    bucket = var.state_bucket_name
    # Key path segments keep environments isolated.
    key    = "database/${var.environment}/terraform.tfstate"
    region = var.aws_region

    # DynamoDB table provides state locking to avoid concurrent apply operations.
    dynamodb_table = var.state_lock_table
    encrypt        = true
  }
}

# Setup instructions:
# 1. aws s3api create-bucket --bucket <bucket> --region <region> --create-bucket-configuration LocationConstraint=<region>
# 2. aws s3api put-bucket-versioning --bucket <bucket> --versioning-configuration Status=Enabled
# 3. aws dynamodb create-table --table-name <table> --attribute-definitions AttributeName=LockID,AttributeType=S \
#       --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST
# 4. aws s3api put-bucket-encryption --bucket <bucket> --server-side-encryption-configuration '... AES256 ...'
