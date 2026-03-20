output "cluster_name" {
  description = "Name of the created Kind cluster"
  value       = kind_cluster.gitops.name
}

output "kubeconfig_path" {
  description = "Path to the generated kubeconfig file for the cluster"
  value       = kind_cluster.gitops.kubeconfig_path
}

output "argocd_namespace" {
  description = "Kubernetes namespace where ArgoCD is installed"
  value       = helm_release.argocd.namespace
}

output "cluster_endpoint" {
  description = "API server endpoint for the Kind cluster"
  value       = kind_cluster.gitops.endpoint
}

output "argocd_version" {
  description = "Installed ArgoCD Helm chart version"
  value       = helm_release.argocd.version
}

output "app_namespaces" {
  description = "List of application namespaces created"
  value       = [for ns in kubernetes_namespace.environments : ns.metadata[0].name]
}

output "argocd_port_forward_command" {
  description = "Command to port-forward ArgoCD UI to localhost:8080"
  value       = "kubectl port-forward svc/argocd-server -n ${helm_release.argocd.namespace} 8080:443"
}

output "argocd_admin_password_command" {
  description = "Command to retrieve the initial ArgoCD admin password"
  value       = "kubectl -n ${helm_release.argocd.namespace} get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
}
