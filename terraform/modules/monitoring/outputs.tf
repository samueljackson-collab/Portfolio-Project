output "flow_log_group_name" {
  description = "CloudWatch log group capturing VPC flow logs"
  value       = try(aws_cloudwatch_log_group.flow_logs[0].name, "")
}

output "flow_log_role_arn" {
  description = "IAM role ARN used by VPC flow logs"
  value       = try(aws_iam_role.flow_logs[0].arn, "")
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = try(aws_sns_topic.alerts[0].arn, "")
}

output "rds_cpu_alarm_name" {
  description = "Name of the RDS CPU alarm"
  value       = try(aws_cloudwatch_metric_alarm.rds_cpu[0].alarm_name, "")
}
