variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID to attach monitoring resources"
  type        = string
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention"
  type        = number
  default     = 30
}

variable "sns_subscribers" {
  description = "List of email addresses subscribed to the SNS topic"
  type        = list(string)
  default     = []
}

variable "rds_instance_arn" {
  description = "ARN of the RDS instance to monitor"
  type        = string
  default     = ""
}

variable "rds_instance_id" {
  description = "ID of the RDS instance"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to monitoring resources"
  type        = map(string)
  default     = {}
}
