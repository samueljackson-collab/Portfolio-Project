output "network_summary" {
  description = "Summarized network settings"
  value = {
    name       = var.name
    cidr_block = var.cidr_block
    tags       = var.tags
  }
}
