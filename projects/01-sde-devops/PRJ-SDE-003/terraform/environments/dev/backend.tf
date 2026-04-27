terraform {
  backend "s3" {
    bucket         = "changeme-terraform-state"
    key            = "prj-sde-003/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "changeme-terraform-locks"
    encrypt        = true
  }
}
