variable "enable_metrics" {
  description = "Enable Prometheus"
  type        = bool
  default     = true
}

variable "enable_logs" {
  description = "Enable log aggregation"
  type        = bool
  default     = true
}

variable "enable_traces" {
  description = "Enable distributed tracing"
  type        = bool
  default     = true
}
