output "assets_bucket_name" {
  description = "Name of the S3 bucket for application assets"
  value       = aws_s3_bucket.assets.bucket
}

output "app_log_group_name" {
  description = "Application CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.app.name
}

output "rds_endpoint" {
  description = "RDS endpoint when created"
  value       = try(aws_db_instance.this[0].address, null)
}

output "rds_identifier" {
  description = "Identifier of the RDS instance"
  value       = try(aws_db_instance.this[0].id, null)
}

output "rds_username" {
  description = "Database username"
  value       = var.db_username
}

output "rds_password" {
  description = "Database password (generated when not provided)"
  value       = try(aws_db_instance.this[0].password, local.db_password_safe)
  sensitive   = true
}
