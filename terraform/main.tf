provider "aws" {
  region = var.aws_region
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  common_tags = {
    Project = var.project_tag
    Owner   = "samueljackson-collab"
    Env     = terraform.workspace
  }
}

resource "aws_s3_bucket" "app_assets" {
  bucket = "${var.project_tag}-assets-${random_id.bucket_suffix.hex}"
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

  tags = merge(local.common_tags, { "Name" = "app-assets" })
}

output "assets_bucket" {
  description = "S3 bucket used for app assets"
  value       = aws_s3_bucket.app_assets.bucket
}
