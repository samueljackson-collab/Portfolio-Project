# Compliant Terraform Module — S3 Encrypted Bucket
# Demonstrates all IaC standards from the Engineer's Handbook:
#   ✅ Named local values for DRY tagging
#   ✅ Encryption enabled (AES-256)
#   ✅ Versioning enabled
#   ✅ Public access blocked
#   ✅ Lifecycle policy (cost management)
#   ✅ Logging enabled
#   ✅ Outputs with descriptions

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
  }

  bucket_name = "${var.project_name}-${var.environment}-${var.purpose}"
}

resource "aws_s3_bucket" "this" {
  bucket        = local.bucket_name
  force_destroy = var.environment != "prod"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

resource "aws_s3_bucket_logging" "this" {
  count = var.log_bucket_id != "" ? 1 : 0

  bucket        = aws_s3_bucket.this.id
  target_bucket = var.log_bucket_id
  target_prefix = "${local.bucket_name}/"
}
