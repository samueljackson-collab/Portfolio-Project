output "alb_dns_name" {
  value       = module.compute.alb_dns_name
  description = "Application load balancer DNS"
}

output "app_asg_name" {
  value       = module.compute.asg_name
  description = "Auto Scaling Group name"
}

output "db_endpoint" {
  value       = module.database.db_endpoint
  description = "Database endpoint"
}

output "artifact_bucket" {
  value       = module.storage.bucket_name
  description = "Primary artifact bucket"
}
