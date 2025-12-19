output "assets_bucket_name" {
  description = "Name of the S3 bucket used for application assets"
  value       = aws_s3_bucket.app.bucket
}

output "rds_endpoint" {
  description = "RDS endpoint when created"
  value       = try(aws_db_instance.postgres[0].address, "")
  sensitive   = true
}

output "rds_identifier" {
  description = "Identifier of the RDS instance"
  value       = try(aws_db_instance.postgres[0].id, "")
}

output "rds_instance_arn" {
  description = "ARN of the RDS instance"
  value       = try(aws_db_instance.postgres[0].arn, "")
}
