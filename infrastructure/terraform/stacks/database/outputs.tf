/**
 * Stack outputs exported for consumers (applications, observability, pipelines).
 */
/**
 * Outputs from the module are wrapped so downstream applications can consume connection metadata.
 */
output "db_endpoint" {
  description = "Reader/Writer endpoint for the PostgreSQL instance."
  value       = module.database.db_endpoint
}

output "db_security_group_id" {
  description = "Identifier for the database security group used to authorize application ingress."
  value       = module.database.db_security_group_id
}

output "db_instance_arn" {
  description = "Amazon Resource Name of the RDS instance for monitoring integrations."
  value       = module.database.db_instance_arn
}

output "connection_string" {
  description = "Pre-formatted PostgreSQL URI for application configuration files."
  value       = "postgresql://${var.db_username}:${var.db_password}@${module.database.db_endpoint}:5432/postgres"
  sensitive   = true
}

# Provide visibility into the AZ distribution for reporting or compliance documentation.
output "availability_zones" {
  description = "Availability zones covered by the database subnet group."
  value       = local.availability_zones
}
