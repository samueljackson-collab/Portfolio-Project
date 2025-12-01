output "vpc_log_group_name" {
  description = "Name of the VPC flow log group"
  value       = aws_cloudwatch_log_group.vpc.name
}

output "flow_log_id" {
  description = "ID of the VPC flow log"
  value       = try(aws_flow_log.this[0].id, "")
}

output "alert_topic_arn" {
  description = "SNS topic used for monitoring alerts"
  value       = aws_sns_topic.alerts.arn
}

output "rds_cpu_alarm_name" {
  description = "Name of the RDS CPU alarm"
  value       = try(aws_cloudwatch_metric_alarm.rds_cpu[0].alarm_name, "")
}
