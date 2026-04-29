terraform {
  required_version = ">= 1.4.0"
}

resource "null_resource" "observability_stack" {
  triggers = {
    metrics_enabled = tostring(var.enable_metrics)
    logs_enabled    = tostring(var.enable_logs)
    traces_enabled  = tostring(var.enable_traces)
  }
}
