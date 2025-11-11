# SNS Module Outputs

output "topic_arn" {
  description = "ARN of the SNS topic"
  value       = aws_sns_topic.security_alerts.arn
}

output "topic_name" {
  description = "Name of the SNS topic"
  value       = aws_sns_topic.security_alerts.name
}

output "topic_id" {
  description = "ID of the SNS topic"
  value       = aws_sns_topic.security_alerts.id
}

output "slack_lambda_arn" {
  description = "ARN of the Slack forwarder Lambda function"
  value       = var.slack_webhook_url != null ? aws_lambda_function.slack_forwarder[0].arn : null
}
