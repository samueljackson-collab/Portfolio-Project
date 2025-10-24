output "alb_dns_name" {
  description = "Public DNS name of the application load balancer."
  value       = module.compute.alb_dns_name
}

output "rds_endpoint" {
  description = "Connection endpoint for the PostgreSQL database."
  value       = module.storage.db_endpoint
}
