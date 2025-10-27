output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "alb_security_group_id" {
  description = "Application Load Balancer Security Group ID"
  value       = module.network.alb_security_group_id
}
