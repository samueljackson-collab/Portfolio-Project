terraform {
  required_version = ">= 1.6.0"
  backend "s3" {
    bucket         = "portfolio-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "portfolio-terraform-locks"
    encrypt        = true
  }
}
