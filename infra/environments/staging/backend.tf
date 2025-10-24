terraform {
  backend "s3" {
    bucket = "portfolio-staging-terraform"
    key    = "state/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "portfolio-staging-locks"
  }
}
