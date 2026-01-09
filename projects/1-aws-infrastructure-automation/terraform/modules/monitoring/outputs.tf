###############################################################################
# Monitoring Module - Outputs
###############################################################################

#------------------------------------------------------------------------------
# SNS Topic Outputs
#------------------------------------------------------------------------------

output "sns_topic_arn" {
  description = "The ARN of the SNS alerts topic."
  value       = aws_sns_topic.alerts.arn
}

output "sns_topic_name" {
  description = "The name of the SNS alerts topic."
  value       = aws_sns_topic.alerts.name
}

#------------------------------------------------------------------------------
# CloudWatch Log Group Outputs
#------------------------------------------------------------------------------

output "application_log_group_name" {
  description = "The name of the application log group."
  value       = aws_cloudwatch_log_group.application.name
}

output "application_log_group_arn" {
  description = "The ARN of the application log group."
  value       = aws_cloudwatch_log_group.application.arn
}

output "access_log_group_name" {
  description = "The name of the access log group."
  value       = aws_cloudwatch_log_group.access.name
}

output "access_log_group_arn" {
  description = "The ARN of the access log group."
  value       = aws_cloudwatch_log_group.access.arn
}

output "error_log_group_name" {
  description = "The name of the error log group."
  value       = aws_cloudwatch_log_group.error.name
}

output "error_log_group_arn" {
  description = "The ARN of the error log group."
  value       = aws_cloudwatch_log_group.error.arn
}

#------------------------------------------------------------------------------
# CloudWatch Dashboard Outputs
#------------------------------------------------------------------------------

output "dashboard_name" {
  description = "The name of the CloudWatch dashboard."
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "dashboard_arn" {
  description = "The ARN of the CloudWatch dashboard."
  value       = aws_cloudwatch_dashboard.main.dashboard_arn
}

#------------------------------------------------------------------------------
# CloudWatch Alarm Outputs
#------------------------------------------------------------------------------

output "alarm_arns" {
  description = "Map of alarm names to ARNs."
  value = merge(
    var.alb_arn_suffix != "" && var.create_alarms ? {
      alb_5xx_errors      = aws_cloudwatch_metric_alarm.alb_5xx_errors[0].arn
      alb_response_time   = aws_cloudwatch_metric_alarm.alb_target_response_time[0].arn
    } : {},
    var.alb_arn_suffix != "" && var.target_group_arn_suffix != "" && var.create_alarms ? {
      alb_unhealthy_hosts = aws_cloudwatch_metric_alarm.alb_unhealthy_hosts[0].arn
    } : {},
    var.asg_name != "" && var.create_alarms ? {
      ec2_cpu_high = aws_cloudwatch_metric_alarm.ec2_cpu_high[0].arn
    } : {},
    var.rds_identifier != "" && var.create_alarms ? {
      rds_cpu_high        = aws_cloudwatch_metric_alarm.rds_cpu_high[0].arn
      rds_storage_low     = aws_cloudwatch_metric_alarm.rds_storage_low[0].arn
      rds_connections_high = aws_cloudwatch_metric_alarm.rds_connections_high[0].arn
    } : {},
    var.create_alarms ? {
      application_errors = aws_cloudwatch_metric_alarm.application_errors[0].arn
    } : {}
  )
}

#------------------------------------------------------------------------------
# Metric Filter Outputs
#------------------------------------------------------------------------------

output "error_count_metric_filter_name" {
  description = "The name of the error count metric filter."
  value       = aws_cloudwatch_log_metric_filter.error_count.name
}
