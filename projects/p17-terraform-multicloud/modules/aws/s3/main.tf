locals {
  tags = merge(var.tags, { Project = var.project_name, Environment = var.environment })
}

resource "aws_s3_bucket" "this" {
  bucket        = var.bucket_name
  force_destroy = var.force_destroy

  tags = merge(local.tags, { Name = var.bucket_name })
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_id == null ? "AES256" : "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
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
  count  = length(var.lifecycle_rules) > 0 ? 1 : 0
  bucket = aws_s3_bucket.this.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.enabled ? "Enabled" : "Disabled"

      dynamic "transition" {
        for_each = rule.value.transition_days == null ? [] : [rule.value]
        content {
          days          = transition.value.transition_days
          storage_class = transition.value.transition_storage_class
        }
      }

      dynamic "expiration" {
        for_each = rule.value.expiration_days == null ? [] : [rule.value]
        content {
          days = expiration.value.expiration_days
        }
      }
    }
  }
}

resource "aws_s3_bucket_logging" "this" {
  count         = var.logging == null ? 0 : 1
  bucket        = aws_s3_bucket.this.id
  target_bucket = var.logging.target_bucket
  target_prefix = var.logging.target_prefix
}

resource "aws_s3_bucket_replication_configuration" "this" {
  count  = var.replication == null ? 0 : 1
  bucket = aws_s3_bucket.this.id
  role   = var.replication.role_arn

  rule {
    status = "Enabled"

    destination {
      bucket        = var.replication.destination_bucket_arn
      storage_class = var.replication.storage_class
    }
  }
}

resource "aws_s3_bucket_policy" "this" {
  count  = var.bucket_policy_json == null ? 0 : 1
  bucket = aws_s3_bucket.this.id
  policy = var.bucket_policy_json
}
