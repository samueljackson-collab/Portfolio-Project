terraform {
  backend "s3" {
    bucket = "portfolio-dev-tfstate"
    key    = "terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "portfolio-dev-locks"
  }
}
