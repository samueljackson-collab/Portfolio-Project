terraform {
  backend "s3" {
    # Backend configuration values are provided via -backend-config flags during terraform init
    # These map to variables: bucket = ${var.tfstate_bucket}, region = ${var.aws_region}
    # See .github/workflows/terraform.yml for backend-config usage
    bucket         = "REPLACE_ME_tfstate_bucket"
    key            = "twisted-monk/terraform.tfstate"
    region         = "REPLACE_ME_aws_region"
    dynamodb_table = "REPLACE_ME_tfstate_lock_table"
    encrypt        = true
  }
}
