# Terraform Backend Configuration
# 
# This configuration uses PARTIAL BACKEND CONFIG for flexibility.
# The actual bucket name, region, and table are provided at runtime via:
#
# Option 1: Environment variables (recommended for local development)
#   export TF_CLI_ARGS_init="-backend-config=bucket=YOUR-BUCKET -backend-config=region=YOUR-REGION -backend-config=dynamodb_table=YOUR-TABLE"
#   terraform init
#
# Option 2: CLI flags (one-time setup)
#   terraform init \
#     -backend-config="bucket=YOUR-BUCKET-NAME" \
#     -backend-config="region=YOUR-REGION" \
#     -backend-config="dynamodb_table=YOUR-TABLE-NAME"
#
# Option 3: Backend config file (recommended for team/CI)
#   Create backend.hcl with:
#     bucket         = "your-bucket-name"
#     key            = "twisted-monk/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "your-table-name"
#     encrypt        = true
#   Then run: terraform init -backend-config=backend.hcl
#
# To create the S3 bucket and DynamoDB table, run:
#   ./scripts/bootstrap_remote_state.sh <bucket-name> <dynamodb-table> <region>

terraform {
  backend "s3" {
    # These values are configured at runtime via -backend-config flags or environment variables
    # See comments above for configuration options
    key     = "twisted-monk/terraform.tfstate"
    encrypt = true
  }
}