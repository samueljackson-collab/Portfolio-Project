# P10 Data Lake Infrastructure with Iceberg

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "p10-datalake"
}

# S3 Buckets
resource "aws_s3_bucket" "bronze" {
  bucket = "${var.project_name}-bronze"
  tags = {
    Project = "P10"
    Zone    = "Bronze"
  }
}

resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.datalake.arn
    }
  }
}

resource "aws_s3_bucket" "silver" {
  bucket = "${var.project_name}-silver"
  tags = {
    Project = "P10"
    Zone    = "Silver"
  }
}

resource "aws_s3_bucket_versioning" "silver" {
  bucket = aws_s3_bucket.silver.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver" {
  bucket = aws_s3_bucket.silver.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.datalake.arn
    }
  }
}

resource "aws_s3_bucket" "gold" {
  bucket = "${var.project_name}-gold"
  tags = {
    Project = "P10"
    Zone    = "Gold"
  }
}

resource "aws_s3_bucket_versioning" "gold" {
  bucket = aws_s3_bucket.gold.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "gold" {
  bucket = aws_s3_bucket.gold.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.datalake.arn
    }
  }
}

# KMS Key
resource "aws_kms_key" "datalake" {
  description             = "KMS key for data lake encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "datalake" {
  name          = "alias/${var.project_name}"
  target_key_id = aws_kms_key.datalake.key_id
}

# Glue Catalog Database
resource "aws_glue_catalog_database" "datalake" {
  name = "${var.project_name}_catalog"
  description = "Iceberg tables for P10 data lake"
}

# IAM Role for Spark/Glue
resource "aws_iam_role" "spark_role" {
  name = "${var.project_name}-spark-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = ["glue.amazonaws.com", "ec2.amazonaws.com"]
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "spark_glue_service" {
  role       = aws_iam_role.spark_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "spark_s3_access" {
  name = "${var.project_name}-s3-access"
  role = aws_iam_role.spark_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.bronze.arn}/*",
          "${aws_s3_bucket.silver.arn}/*",
          "${aws_s3_bucket.gold.arn}/*",
          aws_s3_bucket.bronze.arn,
          aws_s3_bucket.silver.arn,
          aws_s3_bucket.gold.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [aws_kms_key.datalake.arn]
      }
    ]
  })
}

# Lake Formation Settings
resource "aws_lakeformation_data_lake_settings" "datalake" {
  admins = [aws_iam_role.spark_role.arn]
}

# Outputs
output "bronze_bucket" {
  value = aws_s3_bucket.bronze.id
}

output "silver_bucket" {
  value = aws_s3_bucket.silver.id
}

output "gold_bucket" {
  value = aws_s3_bucket.gold.id
}

output "glue_database" {
  value = aws_glue_catalog_database.datalake.name
}

output "spark_role_arn" {
  value = aws_iam_role.spark_role.arn
}
