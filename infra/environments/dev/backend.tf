terraform {
  backend "s3" {
    bucket = "portfolio-dev-terraform"
    key    = "state/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "portfolio-dev-locks"
  }
}
