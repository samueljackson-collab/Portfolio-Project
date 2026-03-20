variable "project_name" {
  description = "Project name used in resource naming and tagging. Must be lowercase alphanumeric."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "project_name must be lowercase alphanumeric and hyphens only."
  }
}

variable "environment" {
  description = "Deployment environment. Controls force_destroy and log level."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "purpose" {
  description = "Bucket purpose suffix (e.g., 'assets', 'backups', 'logs'). Used in bucket name."
  type        = string
  default     = "storage"
}

variable "owner" {
  description = "Team or individual responsible for this resource. Used in Owner tag."
  type        = string
}

variable "log_bucket_id" {
  description = "S3 bucket ID to receive access logs. Leave empty to disable logging."
  type        = string
  default     = ""
}
