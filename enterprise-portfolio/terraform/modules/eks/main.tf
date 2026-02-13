terraform {
  required_version = ">= 1.4.0"
}

resource "null_resource" "eks_cluster" {
  triggers = {
    name    = var.name
    version = var.kubernetes_version
    node_pools = tostring(length(var.node_pools))
  }
}
