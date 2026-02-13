output "monitoring_features" {
  description = "Enabled observability features"
  value = {
    metrics = var.enable_metrics
    logs    = var.enable_logs
    traces  = var.enable_traces
  }
}
