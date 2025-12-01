locals {
  tags = merge(var.tags, { Component = "monitoring" })
}

resource "aws_sns_topic" "alerts" {
  name = "${var.project_tag}-alerts"
  tags = merge(local.tags, { Name = "${var.project_tag}-alerts" })
}

resource "aws_sns_topic_subscription" "email" {
  for_each = toset(var.alarm_emails)

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = each.value
}

resource "aws_cloudwatch_log_group" "managed" {
  for_each = toset(var.log_group_names)

  name              = each.value
  retention_in_days = var.log_retention
  tags              = merge(local.tags, { Name = each.value })
}

resource "aws_cloudwatch_dashboard" "this" {
  dashboard_name = "${var.project_tag}-operations"
  dashboard_body = jsonencode({
    widgets = concat(
      var.rds_identifier != null && var.rds_identifier != "" && var.enable_rds_alarm ? [
        {
          type  = "metric"
          width = 12
          height = 6
          properties = {
            title  = "RDS CPU Utilization"
            region = "${data.aws_region.current.name}"
            metrics = [["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_identifier]]
            view    = "timeSeries"
          }
        },
        {
          type  = "metric"
          width = 12
          height = 6
          properties = {
            title  = "RDS Free Storage"
            region = "${data.aws_region.current.name}"
            metrics = [["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", var.rds_identifier]]
            view    = "timeSeries"
          }
        }
      ] : [],
      [
        {
          type  = "text"
          width = 24
          height = 3
          properties = {
            markdown = "### ${var.project_tag} Operations Dashboard\n- Alerts topic: ${aws_sns_topic.alerts.arn}"
          }
        }
      ]
    )
  })
}

data "aws_region" "current" {}

resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  count = var.enable_rds_alarm && var.rds_identifier != null ? 1 : 0

  alarm_name          = "${var.project_tag}-rds-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "High CPU on RDS instance"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_identifier
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage" {
  count = var.enable_rds_alarm && var.rds_identifier != null ? 1 : 0

  alarm_name          = "${var.project_tag}-rds-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 21474836480 # 20 GB
  alarm_description   = "Low free storage on RDS instance"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_identifier
  }
}
