output "vpc_id" {
  description = "ID of the provisioned VPC"
  value       = module.network.vpc_id
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
  description = "Public DNS name of the load balancer"
  value       = module.network.alb_dns_name
}

output "alb_target_group_arn" {
  description = "ARN of the application load balancer target group"
  value       = module.network.alb_target_group_arn
}

output "alb_security_group_id" {
  description = "Security group ID attached to the application load balancer"
  value       = module.network.alb_security_group_id
}

output "app_autoscaling_group_name" {
  description = "Name of the application auto scaling group"
  value       = module.compute.asg_name
}

output "app_security_group_id" {
  description = "Security group ID applied to application instances"
  value       = module.compute.instance_security_group_id
}

output "rds_endpoint" {
  description = "Database endpoint for application connections"
  value       = module.database.db_endpoint
}

output "rds_security_group_id" {
  description = "Security group ID attached to the RDS instance"
  value       = module.database.db_security_group_id
}
