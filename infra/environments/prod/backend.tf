terraform {
  backend "s3" {
    bucket = "portfolio-prod-terraform"
    key    = "state/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "portfolio-prod-locks"
  }
}
