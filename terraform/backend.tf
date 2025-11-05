terraform {
  backend "s3" {
    bucket         = var.tfstate_bucket
    key            = "twisted-monk/terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = var.tfstate_lock_table
    encrypt        = true
  }
}
