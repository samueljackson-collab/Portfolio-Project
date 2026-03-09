output "cloudformation_execution_role_arn" {
  description = "ARN of the CloudFormation execution role"
  value       = aws_iam_role.cloudformation_execution.arn
}

output "application_role_arn" {
  description = "ARN of the application role"
  value       = aws_iam_role.application.arn
}

output "application_instance_profile_name" {
  description = "Name of the application instance profile"
  value       = aws_iam_instance_profile.application.name
}
