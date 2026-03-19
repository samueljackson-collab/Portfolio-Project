# ============================================================================
# File: infra/environments/prod/outputs.tf
# ============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.network.vpc_cidr
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = module.network.database_subnet_ids
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.compute.alb_dns_name
}

output "alb_url" {
  description = "Application Load Balancer URL"
  value       = "http://${module.compute.alb_dns_name}"
}

output "alb_zone_id" {
  description = "ALB Route53 zone ID"
  value       = module.compute.alb_zone_id
}

output "target_group_arn" {
  description = "Target group ARN"
  value       = module.compute.target_group_arn
}

output "asg_name" {
  description = "Auto Scaling Group name"
  value       = module.compute.asg_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.storage.database_endpoint
  sensitive   = true
}

output "database_identifier" {
  description = "RDS database identifier"
  value       = module.storage.database_identifier
}

output "db_secret_arn" {
  description = "Secrets Manager ARN for database credentials"
  value       = module.storage.db_secret_arn
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = module.storage.s3_bucket_name
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.storage.s3_bucket_arn
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain"
  value       = module.storage.cloudfront_domain
}

output "cloudfront_url" {
  description = "CloudFront distribution URL"
  value       = var.enable_cloudfront ? "https://${module.storage.cloudfront_domain}" : "N/A"
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = module.monitoring.sns_topic_arn
}

output "deployment_summary" {
  description = "Deployment summary information"
  value = {
    environment         = var.environment
    region              = var.aws_region
    vpc_id              = module.network.vpc_id
    alb_url             = "http://${module.compute.alb_dns_name}"
    cloudfront_url      = var.enable_cloudfront ? "https://${module.storage.cloudfront_domain}" : "N/A"
    database_endpoint   = module.storage.database_endpoint
    instance_count      = "${var.asg_min_size}-${var.asg_max_size} instances"
  }
}
