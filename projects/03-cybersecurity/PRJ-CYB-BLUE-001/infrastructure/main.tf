# Root Terraform Configuration for AWS SIEM Pipeline
# Deploys complete security monitoring infrastructure with OpenSearch,
# Kinesis Firehose, Lambda transformation, and log source integration

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration for remote state
  # Uncomment and configure for production use
  # backend "s3" {
  #   bucket         = "my-terraform-state-bucket"
  #   key            = "siem-pipeline/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "Terraform"
      Repository  = "Portfolio-Project"
      Project     = var.project_name
      Environment = var.environment
      Component   = "SIEM"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

#------------------------------------------------------------------------------
# VPC Data Source (use existing VPC or create new one)
#------------------------------------------------------------------------------

data "aws_vpc" "selected" {
  count   = var.create_vpc ? 0 : 1
  id      = var.vpc_id
  default = var.use_default_vpc
}

data "aws_subnets" "private" {
  count = var.create_vpc ? 0 : 1

  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  tags = {
    Tier = "Private"
  }
}

locals {
  vpc_id     = var.create_vpc ? "" : data.aws_vpc.selected[0].id
  vpc_cidr   = var.create_vpc ? "" : data.aws_vpc.selected[0].cidr_block
  subnet_ids = var.create_vpc ? [] : (length(data.aws_subnets.private[0].ids) > 0 ? data.aws_subnets.private[0].ids : var.subnet_ids)
}

#------------------------------------------------------------------------------
# SNS Topic for Security Alerts
#------------------------------------------------------------------------------

resource "aws_sns_topic" "security_alerts" {
  name              = "${var.project_name}-${var.environment}-security-alerts"
  display_name      = "SIEM Security Alerts"
  kms_master_key_id = var.sns_kms_key_id

  tags = {
    Name = "${var.project_name}-${var.environment}-security-alerts"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

#------------------------------------------------------------------------------
# GuardDuty Configuration
#------------------------------------------------------------------------------

resource "aws_guardduty_detector" "main" {
  count  = var.enable_guardduty ? 1 : 0
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = false
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-guardduty"
  }
}

# CloudWatch Log Group for GuardDuty Findings
resource "aws_cloudwatch_log_group" "guardduty" {
  count             = var.enable_guardduty ? 1 : 0
  name              = "/aws/guardduty/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-${var.environment}-guardduty-logs"
  }
}

# EventBridge Rule for GuardDuty Findings
resource "aws_cloudwatch_event_rule" "guardduty" {
  count       = var.enable_guardduty ? 1 : 0
  name        = "${var.project_name}-${var.environment}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-guardduty-rule"
  }
}

# EventBridge Target to CloudWatch Logs
resource "aws_cloudwatch_event_target" "guardduty_logs" {
  count = var.enable_guardduty ? 1 : 0
  rule  = aws_cloudwatch_event_rule.guardduty[0].name
  arn   = aws_cloudwatch_log_group.guardduty[0].arn
}

# CloudWatch Logs Resource Policy for EventBridge
resource "aws_cloudwatch_log_resource_policy" "guardduty" {
  count           = var.enable_guardduty ? 1 : 0
  policy_name     = "${var.project_name}-${var.environment}-guardduty-events"
  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.guardduty[0].arn}:*"
      }
    ]
  })
}

#------------------------------------------------------------------------------
# CloudTrail Configuration
#------------------------------------------------------------------------------

resource "aws_cloudtrail" "main" {
  count                         = var.enable_cloudtrail ? 1 : 0
  name                          = "${var.project_name}-${var.environment}-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail[0].id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.cloudtrail[0].arn}:*"
  cloud_watch_logs_role_arn  = aws_iam_role.cloudtrail[0].arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cloudtrail"
  }

  depends_on = [aws_s3_bucket_policy.cloudtrail]
}

# S3 Bucket for CloudTrail Logs
resource "aws_s3_bucket" "cloudtrail" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-cloudtrail-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.project_name}-${var.environment}-cloudtrail"
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail[0].arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail[0].arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# CloudWatch Log Group for CloudTrail
resource "aws_cloudwatch_log_group" "cloudtrail" {
  count             = var.enable_cloudtrail ? 1 : 0
  name              = "/aws/cloudtrail/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-${var.environment}-cloudtrail-logs"
  }
}

# IAM Role for CloudTrail CloudWatch Logs
resource "aws_iam_role" "cloudtrail" {
  count = var.enable_cloudtrail ? 1 : 0
  name  = "${var.project_name}-${var.environment}-cloudtrail-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-cloudtrail-role"
  }
}

resource "aws_iam_role_policy" "cloudtrail" {
  count = var.enable_cloudtrail ? 1 : 0
  name  = "${var.project_name}-${var.environment}-cloudtrail-policy"
  role  = aws_iam_role.cloudtrail[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.cloudtrail[0].arn}:*"
      }
    ]
  })
}

#------------------------------------------------------------------------------
# OpenSearch Module
#------------------------------------------------------------------------------

module "opensearch" {
  source = "./modules/opensearch"

  project_name = var.project_name
  environment  = var.environment

  vpc_id     = local.vpc_id
  vpc_cidr   = local.vpc_cidr
  subnet_ids = local.subnet_ids

  # Cluster configuration
  engine_version            = var.opensearch_engine_version
  instance_type             = var.opensearch_instance_type
  instance_count            = var.opensearch_instance_count
  zone_awareness_enabled    = var.opensearch_zone_awareness
  availability_zone_count   = var.opensearch_az_count
  dedicated_master_enabled  = var.opensearch_dedicated_master
  dedicated_master_type     = var.opensearch_master_type
  dedicated_master_count    = var.opensearch_master_count

  # Storage
  ebs_volume_type = var.opensearch_ebs_type
  ebs_volume_size = var.opensearch_ebs_size

  # Security
  master_user_name            = var.opensearch_master_user
  master_user_password        = var.opensearch_master_password
  advanced_security_enabled   = true
  internal_user_database_enabled = true

  # Monitoring
  log_retention_days = var.log_retention_days
  alarm_actions      = [aws_sns_topic.security_alerts.arn]

  tags = {
    Component = "OpenSearch"
  }
}

#------------------------------------------------------------------------------
# Kinesis Firehose Module
#------------------------------------------------------------------------------

module "kinesis_firehose" {
  source = "./modules/kinesis-firehose"

  project_name = var.project_name
  environment  = var.environment

  opensearch_domain_arn = module.opensearch.domain_arn
  opensearch_index_name = var.opensearch_index_name

  # Lambda configuration
  lambda_zip_path = var.lambda_zip_path

  # Firehose configuration
  buffer_size     = var.firehose_buffer_size
  buffer_interval = var.firehose_buffer_interval

  # Log source subscriptions
  enable_guardduty_subscription   = var.enable_guardduty
  guardduty_log_group_name        = var.enable_guardduty ? aws_cloudwatch_log_group.guardduty[0].name : ""

  enable_cloudtrail_subscription  = var.enable_cloudtrail
  cloudtrail_log_group_name       = var.enable_cloudtrail ? aws_cloudwatch_log_group.cloudtrail[0].name : ""

  enable_vpc_flow_subscription    = false  # Add VPC Flow Logs configuration if needed
  vpc_flow_log_group_name         = ""

  # Monitoring
  log_retention_days = var.log_retention_days
  alarm_actions      = [aws_sns_topic.security_alerts.arn]

  tags = {
    Component = "LogIngestion"
  }

  depends_on = [module.opensearch]
}
