terraform {
  backend "s3" {
    bucket = "portfolio-prod-tfstate"
    key    = "terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "portfolio-prod-locks"
  }
}
