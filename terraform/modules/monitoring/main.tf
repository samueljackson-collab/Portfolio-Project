locals {
  naming_suffix = "${var.project_tag}-${var.environment}"
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name              = "/aws/vpc/${local.naming_suffix}/flow-logs"
  retention_in_days = var.flow_log_retention_days

  tags = merge(var.tags, { Name = "${var.project_tag}-flow-logs" })
}

data "aws_iam_policy_document" "flow_logs_assume" {
  count = var.enable_flow_logs ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name               = "${local.naming_suffix}-flow-logs"
  assume_role_policy = data.aws_iam_policy_document.flow_logs_assume[0].json

  tags = merge(var.tags, { Name = "${var.project_tag}-flow-logs-role" })
}

data "aws_iam_policy_document" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  statement {
    effect  = "Allow"
    actions = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogGroups", "logs:DescribeLogStreams"]
    resources = [
      aws_cloudwatch_log_group.flow_logs[0].arn,
      "${aws_cloudwatch_log_group.flow_logs[0].arn}:*"
    ]
  }
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name   = "${local.naming_suffix}-flow-logs"
  role   = aws_iam_role.flow_logs[0].id
  policy = data.aws_iam_policy_document.flow_logs[0].json
}

resource "aws_flow_log" "vpc" {
  count = var.enable_flow_logs ? 1 : 0

  log_destination      = aws_cloudwatch_log_group.flow_logs[0].arn
  iam_role_arn         = aws_iam_role.flow_logs[0].arn
  traffic_type         = var.vpc_flow_log_traffic_type
  vpc_id               = var.vpc_id
  log_destination_type = "cloud-watch-logs"
  tags                 = merge(var.tags, { Name = "${var.project_tag}-vpc-flow-logs" })
}

resource "aws_sns_topic" "alerts" {
  count = var.enable_rds_alarms ? 1 : 0

  name = "${local.naming_suffix}-alerts"
  tags = merge(var.tags, { Name = "${var.project_tag}-alerts" })
}

resource "aws_sns_topic_subscription" "email" {
  count = var.enable_rds_alarms && var.alarm_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  count = var.enable_rds_alarms && var.rds_identifier != "" ? 1 : 0

  alarm_name          = "${local.naming_suffix}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.rds_cpu_threshold
  alarm_description   = "Alert when RDS CPU exceeds threshold"

  dimensions = {
    DBInstanceIdentifier = var.rds_identifier
  }

  alarm_actions = var.enable_rds_alarms ? [aws_sns_topic.alerts[0].arn] : []
  ok_actions    = var.enable_rds_alarms ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(var.tags, { Name = "${var.project_tag}-rds-cpu" })
}
