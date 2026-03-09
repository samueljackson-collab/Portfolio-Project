resource "aws_s3_bucket" "state" {
  count  = var.create ? 1 : 0
  bucket = var.bucket_name

  force_destroy = var.force_destroy_bucket

  tags = merge(var.tags, {
    Name = "${var.bucket_name}-state"
  })
}

resource "aws_s3_bucket_versioning" "state" {
  count  = var.create ? 1 : 0
  bucket = aws_s3_bucket.state[0].id

  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  count  = var.create ? 1 : 0
  bucket = aws_s3_bucket.state[0].bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "state_lock" {
  count          = var.create ? 1 : 0
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }

  tags = merge(var.tags, {
    Name = "${var.dynamodb_table_name}-lock"
  })
}
