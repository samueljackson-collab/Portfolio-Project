output "db_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "db_identifier" {
  description = "RDS identifier"
  value       = aws_db_instance.main.id
}

output "db_security_group_ids" {
  description = "Pass-through of DB security group IDs"
  value       = var.db_security_group_ids
}
