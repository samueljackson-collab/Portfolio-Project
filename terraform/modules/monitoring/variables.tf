variable "project_tag" {
  description = "Project tag for naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "Target VPC ID for flow logs"
  type        = string
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

variable "flow_log_retention_days" {
  description = "Retention days for flow log group"
  type        = number
  default     = 30
}

variable "vpc_flow_log_traffic_type" {
  description = "Traffic type captured by flow logs"
  type        = string
  default     = "ALL"
}

variable "enable_rds_alarms" {
  description = "Toggle RDS-related CloudWatch alarms"
  type        = bool
  default     = false
}

variable "rds_identifier" {
  description = "Identifier of the RDS instance for alarms"
  type        = string
  default     = ""
}

variable "alarm_email" {
  description = "Email address for SNS notifications"
  type        = string
  default     = ""
}

variable "rds_cpu_threshold" {
  description = "CPU utilization threshold for alarms"
  type        = number
  default     = 75
}

variable "tags" {
  description = "Common tags to apply"
  type        = map(string)
  default     = {}
}
