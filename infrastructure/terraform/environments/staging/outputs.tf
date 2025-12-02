output "vpc_id" {
  value       = module.network.vpc_id
  description = "VPC identifier"
}

output "alb_dns" {
  value       = module.app.alb_dns_name
  description = "Public DNS for the Application Load Balancer"
}

output "service_cluster" {
  value       = module.app.ecs_cluster_name
  description = "ECS cluster running the orchestration service"
}

output "database_endpoint" {
  value       = module.database.db_endpoint
  description = "PostgreSQL endpoint used by the service"
}
