output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "assets_bucket" {
  description = "S3 bucket used for application assets"
  value       = module.app.assets_bucket_name
}

output "rds_endpoint" {
  description = "RDS endpoint if created"
  value       = module.app.rds_endpoint
}

output "monitoring_topic_arn" {
  description = "SNS topic for monitoring alerts"
  value       = module.monitoring.alert_topic_arn
}
