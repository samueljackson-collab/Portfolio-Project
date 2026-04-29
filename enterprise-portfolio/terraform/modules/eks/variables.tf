variable "name" {
  description = "Cluster name"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "node_pools" {
  description = "Node pool definitions"
  type        = list(object({
    name  = string
    size  = number
    type  = string
  }))
  default = []
}
