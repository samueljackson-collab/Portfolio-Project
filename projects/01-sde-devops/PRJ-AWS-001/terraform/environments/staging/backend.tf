terraform {
  backend "s3" {
    bucket         = "prj-aws-001-terraform-state"
    key            = "staging/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "prj-aws-001-terraform-locks"
    encrypt        = true
  }
}
