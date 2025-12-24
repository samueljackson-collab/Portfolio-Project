output "vpc_id" {
  description = "Identifier of the created VPC."
  value       = module.vpc.vpc_id
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
  description = "Public DNS name of the Application Load Balancer."
  value       = aws_lb.app.dns_name
}

output "alb_target_group_arn" {
  description = "ARN of the ALB target group for the web tier."
  value       = aws_lb_target_group.app.arn
}

output "web_autoscaling_group_name" {
  description = "Name of the web Auto Scaling Group."
  value       = aws_autoscaling_group.web.name
}

output "asset_bucket_name" {
  description = "Name of the S3 bucket used for static assets."
  value       = aws_s3_bucket.assets.bucket
}

output "asset_bucket_arn" {
  description = "ARN of the S3 bucket used for static assets."
  value       = aws_s3_bucket.assets.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution."
  value       = aws_cloudfront_distribution.portfolio.domain_name
}

output "cloudfront_distribution_id" {
  description = "Identifier of the CloudFront distribution."
  value       = aws_cloudfront_distribution.portfolio.id
}
