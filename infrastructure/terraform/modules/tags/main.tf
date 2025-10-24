variable "environment" {
  type        = string
  description = "Deployment environment identifier"
}

variable "service" {
  type        = string
  description = "Service name"
}

locals {
  base_tags = {
    "owner"       = "Sam Jackson"
    "environment" = var.environment
    "service"     = var.service
  }
}

output "common" {
  value = local.base_tags
}
