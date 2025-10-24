# terraform/backend.tf
#
# Remote state configuration - stores Terraform state in S3
# Benefits: Team collaboration, state locking, disaster recovery

# First, create S3 bucket for state storage:
# aws s3 mb s3://YOUR-NAME-terraform-state
# aws s3api put-bucket-versioning --bucket YOUR-NAME-terraform-state --versioning-configuration Status=Enabled
# aws s3api put-bucket-encryption --bucket YOUR-NAME-terraform-state --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Then create DynamoDB table for state locking:
# aws dynamodb create-table \
#   --table-name terraform-state-lock \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

terraform {
  backend "s3" {
    bucket         = "YOUR-NAME-terraform-state"  # Replace with your bucket name
    key            = "portfolio-aws-infra/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"

    # Optional: Use profile if not using default credentials
    # profile = "admin-yourname"
  }
}

