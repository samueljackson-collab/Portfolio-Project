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

output "assets_bucket_name" {
  description = "S3 bucket for application assets"
  value       = module.app.assets_bucket_name
}

output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = module.app.rds_endpoint
  sensitive   = true
}

output "alert_topic_arn" {
  description = "SNS topic used for monitoring alerts"
  value       = module.monitoring.alert_topic_arn
}

output "flow_log_id" {
  description = "VPC flow log ID"
  value       = module.monitoring.flow_log_id
}
