output "security_posture" {
  description = "Security baseline metadata"
  value = {
    frameworks = var.frameworks
    enabled    = var.enabled
  }
}
