# terraform/modules/rds/outputs.tf
output "db_instance_endpoint" {
  description = "Database instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_address" {
  description = "Database instance address"
  value       = aws_db_instance.main.address
}

output "db_security_group_id" {
  description = "Database security group ID"
  value       = aws_security_group.database.id
}

output "db_secret_arn" {
  description = "ARN of the database secret in Secrets Manager"
  value       = aws_secretsmanager_secret.db_password.arn
}
