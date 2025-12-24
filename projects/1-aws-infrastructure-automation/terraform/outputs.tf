output "vpc_id" {
  description = "Identifier of the created VPC."
  value       = module.vpc.vpc_id
}

output "public_subnets" {
  description = "Public subnet IDs for load balancers and ingress."
  value       = module.vpc.public_subnets
}

output "private_subnets" {
  description = "Private subnet IDs for workloads."
  value       = module.vpc.private_subnets
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster."
  value       = module.eks.cluster_name
}

output "rds_endpoint" {
  description = "DNS endpoint for the PostgreSQL database."
  value       = module.rds.db_instance_address
}

output "alb_dns_name" {
  description = "DNS name of the application load balancer."
  value       = module.application_alb.lb_dns_name
}

output "alb_target_group_arn" {
  description = "ARN of the ALB target group used by application instances."
  value       = module.application_alb.target_group_arns["app"]
}

output "app_autoscaling_group_name" {
  description = "Name of the application Auto Scaling Group."
  value       = aws_autoscaling_group.app.name
}

output "static_site_bucket" {
  description = "Name of the static site S3 bucket."
  value       = aws_s3_bucket.static_site.bucket
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain for static and application traffic."
  value       = aws_cloudfront_distribution.portfolio.domain_name
}

output "cloudfront_distribution_id" {
  description = "Identifier of the CloudFront distribution."
  value       = aws_cloudfront_distribution.portfolio.id
}
