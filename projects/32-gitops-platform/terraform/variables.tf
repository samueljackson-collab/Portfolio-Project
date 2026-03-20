variable "cluster_name" {
  description = "Name of the Kind cluster to create"
  type        = string
  default     = "gitops-demo"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*$", var.cluster_name))
    error_message = "Cluster name must start with a lowercase letter and contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "argocd_version" {
  description = "Helm chart version for ArgoCD (argo-cd chart)"
  type        = string
  default     = "5.51.6"
}

variable "node_count" {
  description = "Number of worker nodes in the Kind cluster"
  type        = number
  default     = 2
}

variable "argocd_namespace" {
  description = "Kubernetes namespace where ArgoCD will be installed"
  type        = string
  default     = "argocd"
}

variable "app_namespaces" {
  description = "List of namespaces to create for application workloads"
  type        = list(string)
  default     = ["frontend", "backend", "monitoring"]
}

variable "git_repo_url" {
  description = "Git repository URL for ArgoCD app-of-apps source"
  type        = string
  default     = "https://github.com/samueljackson-collab/Portfolio-Project"
}
