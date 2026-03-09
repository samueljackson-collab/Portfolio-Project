terraform {
  backend "s3" {
    bucket         = "prj-aws-001-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "prj-aws-001-terraform-locks"
    encrypt        = true
  }
}
