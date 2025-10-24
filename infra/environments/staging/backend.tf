terraform {
  backend "s3" {
    bucket = "portfolio-staging-tfstate"
    key    = "terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "portfolio-staging-locks"
  }
}
