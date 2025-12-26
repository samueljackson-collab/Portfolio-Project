output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = module.vpc.internet_gateway_id
}

output "nat_gateway_id" {
  description = "NAT Gateway ID (empty if disabled)"
  value       = module.vpc.nat_gateway_id
}

output "assets_bucket" {
  description = "S3 bucket used for app assets"
  value       = module.app.assets_bucket_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint (empty if RDS not created)"
  value       = module.app.rds_endpoint
}

output "eks_cluster_name" {
  description = "EKS cluster name (empty if not created)"
  value       = module.app.eks_cluster_name
}

output "flow_log_group" {
  description = "CloudWatch log group name for VPC flow logs"
  value       = module.monitoring.flow_log_group_name
}

output "alerts_topic_arn" {
  description = "SNS topic for alerts"
  value       = module.monitoring.sns_topic_arn
}
