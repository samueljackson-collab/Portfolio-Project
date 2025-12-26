# AWS S3 Module

Creates an S3 bucket with versioning, lifecycle rules, encryption, access logging, replication, and optional bucket policy.

## Usage

```hcl
module "logs_bucket" {
  source = "../modules/aws/s3"

  project_name      = "portfolio"
  environment       = "prod"
  bucket_name       = "portfolio-logs"
  versioning_enabled = true
  lifecycle_rules = [
    {
      id                       = "archive"
      enabled                  = true
      transition_days          = 30
      transition_storage_class = "STANDARD_IA"
      expiration_days          = 365
    }
  ]
}
```

## Outputs
- `bucket_id`
- `bucket_arn`
- `bucket_domain_name`
