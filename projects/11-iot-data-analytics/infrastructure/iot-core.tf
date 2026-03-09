# AWS IoT Core Infrastructure for IoT Data Analytics

terraform {
  required_version = ">= 1.0"
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
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "device_count" {
  description = "Number of IoT devices to provision"
  type        = number
  default     = 100
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "iot-analytics"
}

# ==============================================================================
# IoT Core Things (Devices)
# ==============================================================================

resource "aws_iot_thing" "iot_device" {
  count = var.device_count

  name = "${var.project_name}-device-${format("%03d", count.index + 1)}"

  attributes = {
    DeviceType    = "sensor"
    Location      = "datacenter-${count.index % 5 + 1}"
    Manufacturer  = "IoTSolutions"
    Model         = "SENSOR-X100"
  }
}

# ==============================================================================
# IoT Policy
# ==============================================================================

resource "aws_iot_policy" "device_policy" {
  name = "${var.project_name}-device-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:client/$${iot:Connection.Thing.ThingName}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish"
        ]
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic/telemetry/$${iot:Connection.Thing.ThingName}",
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic/telemetry/all"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe"
        ]
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topicfilter/commands/$${iot:Connection.Thing.ThingName}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Receive"
        ]
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic/commands/$${iot:Connection.Thing.ThingName}"
        ]
      }
    ]
  })
}

# ==============================================================================
# IoT Certificates
# ==============================================================================

resource "aws_iot_certificate" "device_cert" {
  count  = var.device_count
  active = true
}

# Attach policy to certificates
resource "aws_iot_policy_attachment" "device_policy_attachment" {
  count = var.device_count

  policy = aws_iot_policy.device_policy.name
  target = aws_iot_certificate.device_cert[count.index].arn
}

# Attach certificate to thing
resource "aws_iot_thing_principal_attachment" "device_cert_attachment" {
  count = var.device_count

  thing     = aws_iot_thing.iot_device[count.index].name
  principal = aws_iot_certificate.device_cert[count.index].arn
}

# ==============================================================================
# IoT Topic Rules
# ==============================================================================

# Rule to forward telemetry to Kinesis Data Firehose
resource "aws_iot_topic_rule" "telemetry_to_firehose" {
  name        = "${replace(var.project_name, "-", "_")}_telemetry_rule"
  description = "Forward IoT telemetry to Kinesis Firehose"
  enabled     = true
  sql         = "SELECT * FROM 'telemetry/+'"
  sql_version = "2016-03-23"

  firehose {
    delivery_stream_name = aws_kinesis_firehose_delivery_stream.iot_telemetry.name
    role_arn            = aws_iam_role.iot_rule_role.arn
    separator           = "\n"
  }

  error_action {
    cloudwatch_logs {
      log_group_name = aws_cloudwatch_log_group.iot_rule_errors.name
      role_arn       = aws_iam_role.iot_rule_role.arn
    }
  }
}

# Rule to detect low battery and trigger SNS alert
resource "aws_iot_topic_rule" "low_battery_alert" {
  name        = "${replace(var.project_name, "-", "_")}_low_battery"
  description = "Alert on low battery levels"
  enabled     = true
  sql         = "SELECT * FROM 'telemetry/+' WHERE battery_level < 20"
  sql_version = "2016-03-23"

  sns {
    message_format = "RAW"
    role_arn      = aws_iam_role.iot_rule_role.arn
    target_arn    = aws_sns_topic.iot_alerts.arn
  }
}

# Rule to detect temperature anomalies
resource "aws_iot_topic_rule" "temp_anomaly" {
  name        = "${replace(var.project_name, "-", "_")}_temp_anomaly"
  description = "Alert on temperature anomalies"
  enabled     = true
  sql         = "SELECT * FROM 'telemetry/+' WHERE temperature > 40 OR temperature < -10"
  sql_version = "2016-03-23"

  sns {
    message_format = "RAW"
    role_arn      = aws_iam_role.iot_rule_role.arn
    target_arn    = aws_sns_topic.iot_alerts.arn
  }
}

# ==============================================================================
# Kinesis Data Firehose
# ==============================================================================

resource "aws_kinesis_firehose_delivery_stream" "iot_telemetry" {
  name        = "${var.project_name}-telemetry-stream"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.iot_data.arn
    prefix     = "telemetry/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    error_output_prefix = "errors/"

    buffer_size     = 5
    buffer_interval = 300

    compression_format = "GZIP"

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_logs.name
      log_stream_name = "S3Delivery"
    }
  }
}

# ==============================================================================
# S3 Bucket for Telemetry Data
# ==============================================================================

resource "aws_s3_bucket" "iot_data" {
  bucket = "${var.project_name}-telemetry-data-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "iot_data_versioning" {
  bucket = aws_s3_bucket.iot_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "iot_data_lifecycle" {
  bucket = aws_s3_bucket.iot_data.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# ==============================================================================
# SNS Topic for Alerts
# ==============================================================================

resource "aws_sns_topic" "iot_alerts" {
  name = "${var.project_name}-alerts"

  tags = {
    Project = var.project_name
  }
}

resource "aws_sns_topic_subscription" "iot_alerts_email" {
  topic_arn = aws_sns_topic.iot_alerts.arn
  protocol  = "email"
  endpoint  = "alerts@example.com" # Replace with actual email
}

# ==============================================================================
# CloudWatch Log Groups
# ==============================================================================

resource "aws_cloudwatch_log_group" "iot_rule_errors" {
  name              = "/aws/iot/${var.project_name}/rule-errors"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "firehose_logs" {
  name              = "/aws/kinesisfirehose/${var.project_name}"
  retention_in_days = 7
}

# ==============================================================================
# IAM Roles and Policies
# ==============================================================================

data "aws_caller_identity" "current" {}

# IoT Rule Role
resource "aws_iam_role" "iot_rule_role" {
  name = "${var.project_name}-iot-rule-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "iot.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "iot_rule_policy" {
  name = "${var.project_name}-iot-rule-policy"
  role = aws_iam_role.iot_rule_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "firehose:PutRecord",
          "firehose:PutRecordBatch"
        ]
        Resource = aws_kinesis_firehose_delivery_stream.iot_telemetry.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.iot_alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.iot_rule_errors.arn}:*"
      }
    ]
  })
}

# Firehose Role
resource "aws_iam_role" "firehose_role" {
  name = "${var.project_name}-firehose-role"

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
}

resource "aws_iam_role_policy" "firehose_policy" {
  name = "${var.project_name}-firehose-policy"
  role = aws_iam_role.firehose_role.id

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
          aws_s3_bucket.iot_data.arn,
          "${aws_s3_bucket.iot_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.firehose_logs.arn}:*"
      }
    ]
  })
}

# ==============================================================================
# Outputs
# ==============================================================================

output "iot_endpoint" {
  description = "AWS IoT Core endpoint"
  value       = data.aws_iot_endpoint.iot_endpoint.endpoint_address
}

output "device_names" {
  description = "List of created device names"
  value       = aws_iot_thing.iot_device[*].name
}

output "s3_bucket" {
  description = "S3 bucket for telemetry data"
  value       = aws_s3_bucket.iot_data.id
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.iot_alerts.arn
}

output "firehose_stream_name" {
  description = "Kinesis Firehose stream name"
  value       = aws_kinesis_firehose_delivery_stream.iot_telemetry.name
}

data "aws_iot_endpoint" "iot_endpoint" {
  endpoint_type = "iot:Data-ATS"
}
