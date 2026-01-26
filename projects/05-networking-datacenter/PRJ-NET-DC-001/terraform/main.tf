terraform {
  required_version = ">= 1.5.0"
}

resource "null_resource" "network_placeholder" {
  triggers = {
    project = var.project_name
    region  = var.region
  }
}
