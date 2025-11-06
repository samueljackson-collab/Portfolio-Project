# Root Terraform Outputs
# These values are displayed after successful terraform apply

output "database_endpoint" {
  description = "Database connection endpoint"
  value       = module.database.db_endpoint
}

output "database_security_group_id" {
  description = "Security group ID for database access"
  value       = module.database.db_security_group_id
}

output "app_security_group_id" {
  description = "Security group ID for application servers"
  value       = aws_security_group.app_servers.id
}

output "connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = "postgresql://${var.db_username}:PASSWORD@${module.database.db_endpoint}:5432/postgres"
  sensitive   = false
}

output "cloudwatch_alarms" {
  description = "CloudWatch alarm names for monitoring"
  value = {
    cpu_utilization = aws_cloudwatch_metric_alarm.database_cpu.alarm_name
    storage_space   = aws_cloudwatch_metric_alarm.database_storage.alarm_name
    connections     = aws_cloudwatch_metric_alarm.database_connections.alarm_name
  }
}

output "next_steps" {
  description = "Post-deployment instructions"
  value       = <<-EOT

  ✅ Database infrastructure deployed successfully!

  Next Steps:
  1. Connect to database: psql "${module.database.db_endpoint}:5432/postgres" -U ${var.db_username}
  2. Create application database: CREATE DATABASE myapp;
  3. Configure application security group rules to allow database access
  4. Set up monitoring alerts (CloudWatch alarms created)
  5. Configure automated backups verification
  6. Review security group rules: ${module.database.db_security_group_id}

  Important:
  - Store db_password securely (use AWS Secrets Manager or Parameter Store)
  - Enable deletion_protection for production: db_deletion_protection = true
  - Enable Multi-AZ for production: db_multi_az = true
  - Set up backup monitoring and testing procedures
  EOT
}
