output "asg_cpu_alarm_name" {
  description = "CloudWatch alarm name for ASG CPU"
  value       = aws_cloudwatch_metric_alarm.asg_cpu.alarm_name
}

output "alb_5xx_alarm_name" {
  description = "CloudWatch alarm name for ALB 5xx"
  value       = aws_cloudwatch_metric_alarm.alb_5xx.alarm_name
}

output "dashboard_name" {
  description = "Operations dashboard name"
  value       = length(aws_cloudwatch_dashboard.main) > 0 ? aws_cloudwatch_dashboard.main[0].dashboard_name : null
}
