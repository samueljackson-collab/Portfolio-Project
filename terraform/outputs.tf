output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.twisted_monk.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = [for s in aws_subnet.public : s.id]
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = [for s in aws_subnet.private : s.id]
}

output "rds_endpoint" {
  description = "RDS instance endpoint (empty if RDS not created)"
  value       = var.create_rds ? aws_db_instance.postgres[0].address : ""
}

output "assets_bucket" {
  description = "S3 bucket used for app assets"
  value       = aws_s3_bucket.app_assets.bucket
}
