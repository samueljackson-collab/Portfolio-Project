output "network" {
  description = "Network module summary"
  value       = module.network.network_summary
}

output "security" {
  description = "Security module summary"
  value       = module.security.security_posture
}

output "monitoring" {
  description = "Observability features"
  value       = module.monitoring.monitoring_features
}

output "eks" {
  description = "Managed Kubernetes cluster metadata"
  value       = module.eks.eks_metadata
}
