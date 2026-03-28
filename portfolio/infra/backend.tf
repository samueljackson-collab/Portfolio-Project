terraform {
  backend "s3" {
    bucket         = "portfolio-terraform-state"
    key            = "portfolio/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "portfolio-terraform-locks"
  }
}
