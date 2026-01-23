output "vpc_id" {
  description = "Identifier of the production VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnets used by the Application Load Balancer."
  value       = module.network.public_subnet_ids
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer fronting the application tier."
  value       = module.alb.alb_dns_name
}

output "alb_security_group_id" {
  description = "Security group protecting the load balancer."
  value       = module.security.alb_security_group_id
}

output "target_group_arn" {
  description = "ARN of the load balancer target group."
  value       = module.alb.target_group_arn
}

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling group serving the application tier."
  value       = module.compute.autoscaling_group_name
}

output "launch_template_id" {
  description = "Launch template used by the Auto Scaling group."
  value       = module.compute.launch_template_id
}

output "rds_endpoint" {
  description = "Writer endpoint for the PostgreSQL database."
  value       = module.database.db_endpoint
}

output "rds_secret_arn" {
  description = "Secrets Manager ARN containing PostgreSQL credentials."
  value       = module.database.db_secret_arn
}

output "rds_instance_id" {
  description = "Identifier of the PostgreSQL instance managed by RDS."
  value       = module.database.db_instance_id
}

output "alerts_topic_arn" {
  description = "SNS topic ARN that receives monitoring alerts."
  value       = module.monitoring.alerts_topic_arn
}
