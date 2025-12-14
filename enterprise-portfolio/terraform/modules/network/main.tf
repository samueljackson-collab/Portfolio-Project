terraform {
  required_version = ">= 1.4.0"
}

resource "null_resource" "network_plan" {
  triggers = {
    cidr_block = var.cidr_block
    name       = var.name
  }
}
