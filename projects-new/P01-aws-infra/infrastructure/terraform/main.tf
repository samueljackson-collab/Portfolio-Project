terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AWS Infrastructure Automation"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

locals {
  project_slug = lower(replace(var.project_name, " ", "-"))
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "logs" {
  description = "KMS key protecting application logs and secrets"
  deletion_window_in_days = 7
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/aws-infra/${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.logs.arn
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "${local.project_slug}-${var.environment}-artifacts"
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.logs.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role" "app" {
  name = "${local.project_slug}-${var.environment}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = ["lambda.amazonaws.com", "ecs-tasks.amazonaws.com"]
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "app" {
  name        = "${local.project_slug}-${var.environment}-policy"
  description = "Least-privilege policy for AWS infra automation"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListAllMyBuckets", "s3:GetBucketLocation"],
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["secretsmanager:DescribeSecret"],
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["cloudwatch:PutMetricData"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app" {
  role       = aws_iam_role.app.name
  policy_arn = aws_iam_policy.app.arn
}

resource "aws_ssm_parameter" "api_key" {
  name   = "/aws-infra/${var.environment}/api-key"
  type   = "SecureString"
  value  = var.api_key_value
  key_id = aws_kms_key.logs.arn
}

resource "aws_cloudwatch_dashboard" "golden_signals" {
  dashboard_name = "aws-infra-${var.environment}"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x    = 0
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWSInfra/Custom", "RequestLatency", "Environment", var.environment]
          ]
          period = 60
          stat   = "p99"
          title  = "API Latency"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "custom_metric_high" {
  alarm_name          = "aws-infra-${var.environment}-custom-metric-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CustomErrors"
  namespace           = "AWSInfra/Custom"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Alert when custom error metric breaches threshold"
  treat_missing_data  = "breaching"
}

output "artifacts_bucket" {
  description = "S3 bucket used for build artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "app_role_arn" {
  description = "IAM role that workloads assume for AWS access"
  value       = aws_iam_role.app.arn
}
