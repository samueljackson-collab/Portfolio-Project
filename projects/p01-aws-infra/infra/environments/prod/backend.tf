terraform {
  backend "s3" {
    bucket         = "CHANGE_ME-terraform-state"
    key            = "p01/prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "CHANGE_ME-terraform-locks"
    encrypt        = true
  }
}

