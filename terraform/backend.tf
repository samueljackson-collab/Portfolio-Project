terraform {
  backend "s3" {
    # Replace the following values with your actual backend configuration.
    bucket         = "REPLACE_ME_tfstate_bucket"
    key            = "twisted-monk/terraform.tfstate"
    region         = "REPLACE_ME_aws_region"
    dynamodb_table = "REPLACE_ME_tfstate_lock_table"
    encrypt        = true
  }
}
