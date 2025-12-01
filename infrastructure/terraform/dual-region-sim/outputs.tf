output "primary_vpc_id" {
  value       = module.primary_vpc.vpc_id
  description = "Primary region VPC id"
}

output "secondary_vpc_id" {
  value       = module.secondary_vpc.vpc_id
  description = "Secondary region VPC id"
}

output "primary_service_url" {
  value       = module.primary_app.load_balancer_dns
  description = "Endpoint for primary roaming service"
}

output "secondary_service_url" {
  value       = module.secondary_app.load_balancer_dns
  description = "Endpoint for secondary roaming service"
}
