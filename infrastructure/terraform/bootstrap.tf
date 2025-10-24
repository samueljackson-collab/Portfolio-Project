resource "aws_s3_bucket" "state" {
  bucket = var.backend_bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-tf-state"
  })
}

resource "aws_dynamodb_table" "locks" {
  name         = var.backend_lock_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-tf-locks"
  })
}

variable "backend_bucket_name" {
  type        = string
  description = "S3 bucket for Terraform state"
}

variable "backend_lock_table" {
  type        = string
  description = "DynamoDB table for Terraform state locking"
}
