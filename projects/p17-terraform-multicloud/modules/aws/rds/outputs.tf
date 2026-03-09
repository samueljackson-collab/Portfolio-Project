output "db_instance_id" {
  description = "Primary DB instance ID."
  value       = aws_db_instance.primary.id
}

output "db_endpoint" {
  description = "Primary DB endpoint."
  value       = aws_db_instance.primary.endpoint
}

output "replica_endpoints" {
  description = "Read replica endpoints."
  value       = aws_db_instance.replica[*].endpoint
}

output "security_group_id" {
  description = "RDS security group ID."
  value       = aws_security_group.db.id
}

output "secret_arn" {
  description = "Secrets Manager ARN for DB credentials."
  value       = aws_secretsmanager_secret.db.arn
}

output "subnet_group_name" {
  description = "DB subnet group name."
  value       = aws_db_subnet_group.this.name
}
