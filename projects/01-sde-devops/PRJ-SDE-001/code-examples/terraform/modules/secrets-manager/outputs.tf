# =====================================================
# AWS Secrets Manager Module - Outputs
# =====================================================

output "secret_id" {
  description = "ID of the secret"
  value       = aws_secretsmanager_secret.this.id
}

output "secret_arn" {
  description = "ARN of the secret"
  value       = aws_secretsmanager_secret.this.arn
}

output "secret_name" {
  description = "Name of the secret"
  value       = aws_secretsmanager_secret.this.name
}

output "secret_version_id" {
  description = "Version ID of the secret"
  value       = aws_secretsmanager_secret_version.this.version_id
}

# Note: We don't output the actual secret value for security reasons
# To retrieve the secret value, use:
# aws secretsmanager get-secret-value --secret-id <secret_id> --query SecretString --output text

output "rotation_lambda_arn" {
  description = "ARN of the rotation Lambda function (if rotation is enabled)"
  value       = var.enable_rotation ? aws_lambda_function.rotation[0].arn : null
}

output "rotation_enabled" {
  description = "Whether automatic rotation is enabled"
  value       = var.enable_rotation
}

output "rotation_days" {
  description = "Number of days between rotations (if enabled)"
  value       = var.enable_rotation ? var.rotation_days : null
}

# Helper output for database connection strings
# This should be used in other modules to construct connection strings
output "secret_reference" {
  description = "Reference to use in database connection strings"
  value       = "{{resolve:secretsmanager:${aws_secretsmanager_secret.this.name}}}"
}
