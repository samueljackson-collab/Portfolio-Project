###############################################################################
# Monitoring Module - CloudWatch Dashboards, Alarms, and SNS Topics
#
# This module creates comprehensive monitoring resources including:
# - CloudWatch dashboards for infrastructure visualization
# - CloudWatch alarms for critical metrics
# - SNS topics for alert notifications
# - Log groups with retention policies
###############################################################################

terraform {
  required_version = ">= 1.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

#------------------------------------------------------------------------------
# Data Sources
#------------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

#------------------------------------------------------------------------------
# SNS Topic for Alerts
#------------------------------------------------------------------------------

resource "aws_sns_topic" "alerts" {
  name              = "${var.name_prefix}-alerts"
  kms_master_key_id = var.kms_key_id

  tags = var.tags
}

resource "aws_sns_topic_policy" "alerts" {
  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchAlarms"
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "sns:Publish"
        Resource = aws_sns_topic.alerts.arn
        Condition = {
          ArnLike = {
            "aws:SourceArn" = "arn:aws:cloudwatch:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:alarm:*"
          }
        }
      }
    ]
  })
}

resource "aws_sns_topic_subscription" "email" {
  count = length(var.alert_email_addresses)

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_addresses[count.index]
}

#------------------------------------------------------------------------------
# CloudWatch Log Groups
#------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/${var.name_prefix}/application"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "access" {
  name              = "/aws/${var.name_prefix}/access"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "error" {
  name              = "/aws/${var.name_prefix}/error"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id

  tags = var.tags
}

#------------------------------------------------------------------------------
# CloudWatch Dashboard - Infrastructure Overview
#------------------------------------------------------------------------------

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.name_prefix}-infrastructure"

  dashboard_body = jsonencode({
    widgets = concat(
      # Header widget
      [{
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# ${var.name_prefix} Infrastructure Dashboard"
        }
      }],

      # ALB metrics row
      var.alb_arn_suffix != "" ? [
        {
          type   = "metric"
          x      = 0
          y      = 1
          width  = 8
          height = 6
          properties = {
            title  = "ALB Request Count"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix, { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 1
          width  = 8
          height = 6
          properties = {
            title  = "ALB Target Response Time"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", var.alb_arn_suffix, { stat = "Average", period = 60 }],
              ["...", { stat = "p95", period = 60 }],
              ["...", { stat = "p99", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 1
          width  = 8
          height = 6
          properties = {
            title  = "ALB HTTP Errors"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", var.alb_arn_suffix, { stat = "Sum", period = 60 }],
              [".", "HTTPCode_Target_5XX_Count", ".", ".", { stat = "Sum", period = 60 }],
              [".", "HTTPCode_ELB_5XX_Count", ".", ".", { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        }
      ] : [],

      # EC2/ASG metrics row
      var.asg_name != "" ? [
        {
          type   = "metric"
          x      = 0
          y      = 7
          width  = 8
          height = 6
          properties = {
            title  = "ASG Instance Count"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/AutoScaling", "GroupDesiredCapacity", "AutoScalingGroupName", var.asg_name, { stat = "Average", period = 60 }],
              [".", "GroupInServiceInstances", ".", ".", { stat = "Average", period = 60 }],
              [".", "GroupTotalInstances", ".", ".", { stat = "Average", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 7
          width  = 8
          height = 6
          properties = {
            title  = "EC2 CPU Utilization"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/EC2", "CPUUtilization", "AutoScalingGroupName", var.asg_name, { stat = "Average", period = 60 }],
              ["...", { stat = "Maximum", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 7
          width  = 8
          height = 6
          properties = {
            title  = "EC2 Network I/O"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/EC2", "NetworkIn", "AutoScalingGroupName", var.asg_name, { stat = "Sum", period = 60 }],
              [".", "NetworkOut", ".", ".", { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        }
      ] : [],

      # RDS metrics row
      var.rds_identifier != "" ? [
        {
          type   = "metric"
          x      = 0
          y      = 13
          width  = 6
          height = 6
          properties = {
            title  = "RDS CPU Utilization"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_identifier, { stat = "Average", period = 60 }]
            ]
            view   = "timeSeries"
            yAxis  = { left = { min = 0, max = 100 } }
          }
        },
        {
          type   = "metric"
          x      = 6
          y      = 13
          width  = 6
          height = 6
          properties = {
            title  = "RDS Database Connections"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.rds_identifier, { stat = "Average", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 12
          y      = 13
          width  = 6
          height = 6
          properties = {
            title  = "RDS Free Storage Space"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", var.rds_identifier, { stat = "Average", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 18
          y      = 13
          width  = 6
          height = 6
          properties = {
            title  = "RDS Read/Write IOPS"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", var.rds_identifier, { stat = "Average", period = 60 }],
              [".", "WriteIOPS", ".", ".", { stat = "Average", period = 60 }]
            ]
            view = "timeSeries"
          }
        }
      ] : [],

      # VPC/NAT Gateway metrics row
      var.nat_gateway_id != "" ? [
        {
          type   = "metric"
          x      = 0
          y      = 19
          width  = 8
          height = 6
          properties = {
            title  = "NAT Gateway Bytes"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/NATGateway", "BytesInFromSource", "NatGatewayId", var.nat_gateway_id, { stat = "Sum", period = 60 }],
              [".", "BytesOutToDestination", ".", ".", { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 19
          width  = 8
          height = 6
          properties = {
            title  = "NAT Gateway Packets"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/NATGateway", "PacketsInFromSource", "NatGatewayId", var.nat_gateway_id, { stat = "Sum", period = 60 }],
              [".", "PacketsOutToDestination", ".", ".", { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 19
          width  = 8
          height = 6
          properties = {
            title  = "NAT Gateway Connection Count"
            region = data.aws_region.current.name
            metrics = [
              ["AWS/NATGateway", "ActiveConnectionCount", "NatGatewayId", var.nat_gateway_id, { stat = "Average", period = 60 }],
              [".", "ConnectionAttemptCount", ".", ".", { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        }
      ] : [],

      # CloudFront metrics row
      var.cloudfront_distribution_id != "" ? [
        {
          type   = "metric"
          x      = 0
          y      = 25
          width  = 8
          height = 6
          properties = {
            title  = "CloudFront Requests"
            region = "us-east-1"  # CloudFront metrics are always in us-east-1
            metrics = [
              ["AWS/CloudFront", "Requests", "DistributionId", var.cloudfront_distribution_id, "Region", "Global", { stat = "Sum", period = 60 }]
            ]
            view = "timeSeries"
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 25
          width  = 8
          height = 6
          properties = {
            title  = "CloudFront Cache Hit Rate"
            region = "us-east-1"
            metrics = [
              ["AWS/CloudFront", "CacheHitRate", "DistributionId", var.cloudfront_distribution_id, "Region", "Global", { stat = "Average", period = 60 }]
            ]
            view  = "timeSeries"
            yAxis = { left = { min = 0, max = 100 } }
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 25
          width  = 8
          height = 6
          properties = {
            title  = "CloudFront Error Rate"
            region = "us-east-1"
            metrics = [
              ["AWS/CloudFront", "4xxErrorRate", "DistributionId", var.cloudfront_distribution_id, "Region", "Global", { stat = "Average", period = 60 }],
              [".", "5xxErrorRate", ".", ".", ".", ".", { stat = "Average", period = 60 }]
            ]
            view = "timeSeries"
          }
        }
      ] : []
    )
  })
}

#------------------------------------------------------------------------------
# CloudWatch Alarms - ALB
#------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  count = var.alb_arn_suffix != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-alb-5xx-errors"
  alarm_description   = "ALB 5xx error rate is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = var.alb_5xx_threshold

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time" {
  count = var.alb_arn_suffix != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-alb-response-time"
  alarm_description   = "ALB target response time is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = var.alb_response_time_threshold

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_hosts" {
  count = var.alb_arn_suffix != "" && var.target_group_arn_suffix != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-alb-unhealthy-hosts"
  alarm_description   = "ALB has unhealthy target hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 0

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
    TargetGroup  = var.target_group_arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  treat_missing_data = "notBreaching"

  tags = var.tags
}

#------------------------------------------------------------------------------
# CloudWatch Alarms - EC2/ASG
#------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  count = var.asg_name != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-ec2-cpu-high"
  alarm_description   = "EC2 CPU utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = var.ec2_cpu_threshold

  dimensions = {
    AutoScalingGroupName = var.asg_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

#------------------------------------------------------------------------------
# CloudWatch Alarms - RDS
#------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  count = var.rds_identifier != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-rds-cpu-high"
  alarm_description   = "RDS CPU utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.rds_cpu_threshold

  dimensions = {
    DBInstanceIdentifier = var.rds_identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  count = var.rds_identifier != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-rds-storage-low"
  alarm_description   = "RDS free storage space is low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.rds_storage_threshold

  dimensions = {
    DBInstanceIdentifier = var.rds_identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  count = var.rds_identifier != "" && var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-rds-connections-high"
  alarm_description   = "RDS database connections are high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.rds_connections_threshold

  dimensions = {
    DBInstanceIdentifier = var.rds_identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

#------------------------------------------------------------------------------
# CloudWatch Log Metric Filters
#------------------------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "error_count" {
  name           = "${var.name_prefix}-error-count"
  pattern        = "[timestamp, level=ERROR, ...]"
  log_group_name = aws_cloudwatch_log_group.application.name

  metric_transformation {
    name          = "ErrorCount"
    namespace     = "${var.name_prefix}/Application"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "application_errors" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.name_prefix}-application-errors"
  alarm_description   = "Application error rate is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "ErrorCount"
  namespace           = "${var.name_prefix}/Application"
  period              = 300
  statistic           = "Sum"
  threshold           = var.application_error_threshold

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  treat_missing_data = "notBreaching"

  tags = var.tags
}
