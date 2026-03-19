##############################################################################
# RDS Module - outputs.tf
##############################################################################

output "db_instance_endpoint" {
  description = "Connection endpoint for the RDS instance (hostname:port)."
  value       = aws_db_instance.this.endpoint
}

output "db_instance_port" {
  description = "Port number the RDS instance listens on (5432 for PostgreSQL, 3306 for MySQL)."
  value       = aws_db_instance.this.port
}

output "db_instance_id" {
  description = "The RDS instance identifier."
  value       = aws_db_instance.this.id
}

output "db_instance_arn" {
  description = "ARN of the RDS instance."
  value       = aws_db_instance.this.arn
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group associated with the RDS instance."
  value       = aws_db_subnet_group.this.name
}

output "security_group_id" {
  description = "ID of the security group attached to the RDS instance."
  value       = aws_security_group.rds.id
}

output "secret_arn" {
  description = "ARN of the Secrets Manager secret containing the database credentials."
  value       = aws_secretsmanager_secret.db_password.arn
  sensitive   = true
}
