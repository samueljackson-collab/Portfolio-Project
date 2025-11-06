# Kinesis Firehose Module Outputs

output "delivery_stream_name" {
  description = "Name of the Kinesis Firehose delivery stream"
  value       = aws_kinesis_firehose_delivery_stream.siem.name
}

output "delivery_stream_arn" {
  description = "ARN of the Kinesis Firehose delivery stream"
  value       = aws_kinesis_firehose_delivery_stream.siem.arn
}

output "backup_bucket_name" {
  description = "Name of the S3 backup bucket"
  value       = aws_s3_bucket.backup.id
}

output "backup_bucket_arn" {
  description = "ARN of the S3 backup bucket"
  value       = aws_s3_bucket.backup.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda log transformer function"
  value       = aws_lambda_function.log_transformer.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda log transformer function"
  value       = aws_lambda_function.log_transformer.arn
}

output "lambda_log_group_name" {
  description = "CloudWatch log group name for Lambda logs"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "firehose_log_group_name" {
  description = "CloudWatch log group name for Firehose logs"
  value       = aws_cloudwatch_log_group.firehose.name
}

output "firehose_role_arn" {
  description = "IAM role ARN for Firehose"
  value       = aws_iam_role.firehose.arn
}

output "lambda_role_arn" {
  description = "IAM role ARN for Lambda"
  value       = aws_iam_role.lambda.arn
}

output "cloudwatch_logs_role_arn" {
  description = "IAM role ARN for CloudWatch Logs subscription"
  value       = aws_iam_role.cloudwatch_logs.arn
}

output "alarm_names" {
  description = "CloudWatch alarm names for monitoring"
  value = {
    firehose_throttled = aws_cloudwatch_metric_alarm.firehose_throttled.alarm_name
    lambda_errors      = aws_cloudwatch_metric_alarm.lambda_errors.alarm_name
  }
}
