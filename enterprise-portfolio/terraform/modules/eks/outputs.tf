output "eks_metadata" {
  description = "EKS cluster metadata"
  value = {
    name    = var.name
    version = var.kubernetes_version
    node_pools = var.node_pools
  }
}
