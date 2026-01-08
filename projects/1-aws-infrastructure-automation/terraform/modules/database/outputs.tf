###############################################################################
# Database Module - Outputs
###############################################################################

#------------------------------------------------------------------------------
# RDS Instance Outputs
#------------------------------------------------------------------------------

output "db_instance_id" {
  description = "The ID of the RDS instance."
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "The ARN of the RDS instance."
  value       = aws_db_instance.main.arn
}

output "db_instance_identifier" {
  description = "The identifier of the RDS instance."
  value       = aws_db_instance.main.identifier
}

output "db_instance_endpoint" {
  description = "The endpoint of the RDS instance."
  value       = aws_db_instance.main.endpoint
}

output "db_instance_address" {
  description = "The address of the RDS instance."
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "The port of the RDS instance."
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "The database name."
  value       = aws_db_instance.main.db_name
}

output "db_instance_username" {
  description = "The master username."
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "db_instance_status" {
  description = "The status of the RDS instance."
  value       = aws_db_instance.main.status
}

output "db_instance_availability_zone" {
  description = "The availability zone of the RDS instance."
  value       = aws_db_instance.main.availability_zone
}

output "db_instance_multi_az" {
  description = "Whether the RDS instance is multi-AZ."
  value       = aws_db_instance.main.multi_az
}

output "db_instance_engine" {
  description = "The database engine."
  value       = aws_db_instance.main.engine
}

output "db_instance_engine_version" {
  description = "The database engine version."
  value       = aws_db_instance.main.engine_version_actual
}

output "db_instance_class" {
  description = "The instance class of the RDS instance."
  value       = aws_db_instance.main.instance_class
}

output "db_instance_resource_id" {
  description = "The resource ID of the RDS instance."
  value       = aws_db_instance.main.resource_id
}

#------------------------------------------------------------------------------
# Read Replica Outputs
#------------------------------------------------------------------------------

output "replica_instance_id" {
  description = "The ID of the read replica (if created)."
  value       = var.create_read_replica ? aws_db_instance.replica[0].id : null
}

output "replica_instance_endpoint" {
  description = "The endpoint of the read replica (if created)."
  value       = var.create_read_replica ? aws_db_instance.replica[0].endpoint : null
}

output "replica_instance_address" {
  description = "The address of the read replica (if created)."
  value       = var.create_read_replica ? aws_db_instance.replica[0].address : null
}

#------------------------------------------------------------------------------
# Security Group Outputs
#------------------------------------------------------------------------------

output "security_group_id" {
  description = "The ID of the RDS security group."
  value       = aws_security_group.rds.id
}

output "security_group_arn" {
  description = "The ARN of the RDS security group."
  value       = aws_security_group.rds.arn
}

#------------------------------------------------------------------------------
# Parameter Group Outputs
#------------------------------------------------------------------------------

output "parameter_group_name" {
  description = "The name of the parameter group."
  value       = aws_db_parameter_group.main.name
}

output "parameter_group_arn" {
  description = "The ARN of the parameter group."
  value       = aws_db_parameter_group.main.arn
}

#------------------------------------------------------------------------------
# KMS Key Outputs
#------------------------------------------------------------------------------

output "kms_key_id" {
  description = "The ID of the KMS key used for encryption."
  value       = var.create_kms_key ? aws_kms_key.rds[0].key_id : var.kms_key_id
}

output "kms_key_arn" {
  description = "The ARN of the KMS key used for encryption."
  value       = var.create_kms_key ? aws_kms_key.rds[0].arn : null
}

#------------------------------------------------------------------------------
# Connection String Outputs
#------------------------------------------------------------------------------

output "connection_string" {
  description = "PostgreSQL connection string (without password)."
  value       = "postgresql://${aws_db_instance.main.username}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "jdbc_connection_string" {
  description = "JDBC connection string."
  value       = "jdbc:postgresql://${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
}

#------------------------------------------------------------------------------
# Monitoring Outputs
#------------------------------------------------------------------------------

output "enhanced_monitoring_arn" {
  description = "The ARN of the enhanced monitoring IAM role."
  value       = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null
}

#------------------------------------------------------------------------------
# CloudWatch Alarm Outputs
#------------------------------------------------------------------------------

output "cloudwatch_alarm_arns" {
  description = "List of CloudWatch alarm ARNs."
  value = var.create_cloudwatch_alarms ? [
    aws_cloudwatch_metric_alarm.cpu_utilization[0].arn,
    aws_cloudwatch_metric_alarm.free_storage[0].arn,
    aws_cloudwatch_metric_alarm.database_connections[0].arn,
    aws_cloudwatch_metric_alarm.freeable_memory[0].arn
  ] : []
}
