output "vpc_id" {
  description = "ID of the VPC"
  value       = module.network.vpc_id
}

output "alb_dns_name" {
  description = "DNS name for the Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "rds_endpoint" {
  description = "Endpoint of the RDS database"
  value       = module.storage.rds_endpoint
}

output "cloudfront_domain_name" {
  description = "Domain name for CloudFront distribution"
  value       = module.storage.cloudfront_domain_name
}

output "artifacts_bucket_name" {
  description = "Artifacts bucket"
  value       = module.storage.artifacts_bucket_name
}

