output "alerts_topic_arn" {
  description = "ARN of the SNS topic that receives monitoring alerts."
  value       = aws_sns_topic.alerts.arn
}
