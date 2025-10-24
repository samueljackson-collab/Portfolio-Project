# Terraform state backend configuration
# Stores state in S3 with DynamoDB locking

terraform {
  backend "s3" {
    bucket         = "portfolio-terraform-state"  # Must be globally unique
    key            = "portfolio/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "portfolio-terraform-locks"
  }
}
