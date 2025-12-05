output "placeholder_id" {
  description = "Identifier proving Terraform state is wired up"
  value       = null_resource.network_placeholder.id
}
