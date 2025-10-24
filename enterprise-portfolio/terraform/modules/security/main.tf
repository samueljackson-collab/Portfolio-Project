terraform {
  required_version = ">= 1.4.0"
}

resource "null_resource" "security_baseline" {
  triggers = {
    framework = join(",", var.frameworks)
  }
}
