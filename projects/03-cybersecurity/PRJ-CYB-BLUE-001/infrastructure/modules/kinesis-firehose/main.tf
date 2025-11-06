# Kinesis Firehose Module for SIEM Log Ingestion
# Delivers logs from CloudWatch to OpenSearch via Lambda transformation

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    var.tags,
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "SIEM-Ingestion"
    }
  )
}

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

#------------------------------------------------------------------------------
# S3 Bucket for Failed Records Backup
#------------------------------------------------------------------------------

resource "aws_s3_bucket" "backup" {
  bucket = "${local.name_prefix}-siem-backup-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-siem-backup"
    }
  )
}

resource "aws_s3_bucket_versioning" "backup" {
  bucket = aws_s3_bucket.backup.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup" {
  bucket = aws_s3_bucket.backup.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backup" {
  bucket = aws_s3_bucket.backup.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "backup" {
  bucket = aws_s3_bucket.backup.id

  rule {
    id     = "delete-old-backups"
    status = "Enabled"

    expiration {
      days = var.backup_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.backup_retention_days
    }
  }
}

#------------------------------------------------------------------------------
# Lambda Function for Log Transformation
#------------------------------------------------------------------------------

resource "aws_lambda_function" "log_transformer" {
  filename      = var.lambda_zip_path
  function_name = "${local.name_prefix}-log-transformer"
  role          = aws_iam_role.lambda.arn
  handler       = "log_transformer.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 512

  # Publish a version for stable deployments (avoid using $LATEST in production)
  publish       = true

  environment {
    variables = {
      LOG_LEVEL = var.lambda_log_level
    }
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-log-transformer"
    }
  )
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.log_transformer.function_name}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

#------------------------------------------------------------------------------
# IAM Role for Lambda
#------------------------------------------------------------------------------

resource "aws_iam_role" "lambda" {
  name = "${local.name_prefix}-lambda-transformer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

#------------------------------------------------------------------------------
# IAM Role for Kinesis Firehose
#------------------------------------------------------------------------------

resource "aws_iam_role" "firehose" {
  name = "${local.name_prefix}-firehose-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "firehose.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "firehose" {
  name = "${local.name_prefix}-firehose-policy"
  role = aws_iam_role.firehose.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.backup.arn,
          "${aws_s3_bucket.backup.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunctionConfiguration"
        ]
        Resource = aws_lambda_function.log_transformer.arn
      },
      {
        Effect = "Allow"
        Action = [
          "es:DescribeElasticsearchDomain",
          "es:DescribeElasticsearchDomainConfig",
          "es:ESHttpGet",
          "es:ESHttpPut",
          "es:ESHttpPost"
        ]
        Resource = [
          var.opensearch_domain_arn,
          "${var.opensearch_domain_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents"
        ]
        Resource = aws_cloudwatch_log_group.firehose.arn
      }
    ]
  })
}

#------------------------------------------------------------------------------
# CloudWatch Log Group for Firehose
#------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "firehose" {
  name              = "/aws/kinesisfirehose/${local.name_prefix}-siem"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

resource "aws_cloudwatch_log_stream" "firehose_destination" {
  name           = "DestinationDelivery"
  log_group_name = aws_cloudwatch_log_group.firehose.name
}

resource "aws_cloudwatch_log_stream" "firehose_backup" {
  name           = "BackupDelivery"
  log_group_name = aws_cloudwatch_log_group.firehose.name
}

#------------------------------------------------------------------------------
# Kinesis Firehose Delivery Stream
#------------------------------------------------------------------------------

resource "aws_kinesis_firehose_delivery_stream" "siem" {
  name        = "${local.name_prefix}-siem-stream"
  destination = "elasticsearch"

  elasticsearch_configuration {
    domain_arn = var.opensearch_domain_arn
    role_arn   = aws_iam_role.firehose.arn
    index_name = var.opensearch_index_name

    index_rotation_period = var.index_rotation_period

    buffering_interval = var.buffer_interval
    buffering_size     = var.buffer_size

    retry_duration = var.retry_duration

    s3_backup_mode = "FailedDocumentsOnly"

    s3_configuration {
      role_arn           = aws_iam_role.firehose.arn
      bucket_arn         = aws_s3_bucket.backup.arn
      prefix             = "failed/"
      error_output_prefix = "errors/"
      buffering_size     = 5
      buffering_interval = 300
      compression_format = "GZIP"
    }

    processing_configuration {
      enabled = true

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          # Use qualified_arn for published version instead of $LATEST for stability
          parameter_value = aws_lambda_function.log_transformer.qualified_arn
        }

        parameters {
          parameter_name  = "NumberOfRetries"
          parameter_value = "3"
        }

        parameters {
          parameter_name  = "BufferSizeInMBs"
          parameter_value = "3"
        }

        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = "60"
        }
      }
    }

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose.name
      log_stream_name = aws_cloudwatch_log_stream.firehose_destination.name
    }
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-siem-stream"
    }
  )

  depends_on = [
    aws_iam_role_policy.firehose
  ]
}

#------------------------------------------------------------------------------
# CloudWatch Logs Subscription Filter
#------------------------------------------------------------------------------

resource "aws_cloudwatch_log_subscription_filter" "guardduty" {
  count           = var.enable_guardduty_subscription ? 1 : 0
  name            = "${local.name_prefix}-guardduty-subscription"
  log_group_name  = var.guardduty_log_group_name
  filter_pattern  = ""
  destination_arn = aws_kinesis_firehose_delivery_stream.siem.arn
  role_arn        = aws_iam_role.cloudwatch_logs.arn
}

resource "aws_cloudwatch_log_subscription_filter" "vpc_flow_logs" {
  count           = var.enable_vpc_flow_subscription ? 1 : 0
  name            = "${local.name_prefix}-vpc-flow-subscription"
  log_group_name  = var.vpc_flow_log_group_name
  filter_pattern  = ""
  destination_arn = aws_kinesis_firehose_delivery_stream.siem.arn
  role_arn        = aws_iam_role.cloudwatch_logs.arn
}

resource "aws_cloudwatch_log_subscription_filter" "cloudtrail" {
  count           = var.enable_cloudtrail_subscription ? 1 : 0
  name            = "${local.name_prefix}-cloudtrail-subscription"
  log_group_name  = var.cloudtrail_log_group_name
  filter_pattern  = ""
  destination_arn = aws_kinesis_firehose_delivery_stream.siem.arn
  role_arn        = aws_iam_role.cloudwatch_logs.arn
}

#------------------------------------------------------------------------------
# IAM Role for CloudWatch Logs Subscription
#------------------------------------------------------------------------------

resource "aws_iam_role" "cloudwatch_logs" {
  name = "${local.name_prefix}-cloudwatch-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "cloudwatch_logs" {
  name = "${local.name_prefix}-cloudwatch-logs-policy"
  role = aws_iam_role.cloudwatch_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "firehose:PutRecord",
          "firehose:PutRecordBatch"
        ]
        Resource = aws_kinesis_firehose_delivery_stream.siem.arn
      }
    ]
  })
}

#------------------------------------------------------------------------------
# CloudWatch Alarms
#------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "firehose_throttled" {
  alarm_name          = "${local.name_prefix}-firehose-throttled"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ThrottledRecords"
  namespace           = "AWS/Firehose"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Firehose delivery stream is being throttled"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DeliveryStreamName = aws_kinesis_firehose_delivery_stream.siem.name
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.name_prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Lambda log transformer is experiencing errors"
  alarm_actions       = var.alarm_actions

  dimensions = {
    FunctionName = aws_lambda_function.log_transformer.function_name
  }

  tags = local.common_tags
}
