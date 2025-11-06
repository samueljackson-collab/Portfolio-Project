# Kinesis Firehose Module Variables

variable "project_name" {
  type        = string
  description = "Project identifier for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "opensearch_domain_arn" {
  type        = string
  description = "ARN of the OpenSearch domain"
}

variable "opensearch_index_name" {
  type        = string
  description = "Name of the OpenSearch index"
  default     = "security-events"
}

variable "index_rotation_period" {
  type        = string
  description = "Frequency of index rotation (NoRotation, OneHour, OneDay, OneWeek, OneMonth)"
  default     = "OneDay"

  validation {
    condition     = contains(["NoRotation", "OneHour", "OneDay", "OneWeek", "OneMonth"], var.index_rotation_period)
    error_message = "Index rotation period must be NoRotation, OneHour, OneDay, OneWeek, or OneMonth"
  }
}

#------------------------------------------------------------------------------
# Lambda Configuration
#------------------------------------------------------------------------------

variable "lambda_zip_path" {
  type        = string
  description = "Path to Lambda function ZIP file"
}

variable "lambda_log_level" {
  type        = string
  description = "Log level for Lambda function"
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.lambda_log_level)
    error_message = "Lambda log level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL"
  }
}

#------------------------------------------------------------------------------
# Firehose Configuration
#------------------------------------------------------------------------------

variable "buffer_size" {
  type        = number
  description = "Buffer size in MB before flushing to OpenSearch"
  default     = 5

  validation {
    condition     = var.buffer_size >= 1 && var.buffer_size <= 100
    error_message = "Buffer size must be between 1 and 100 MB"
  }
}

variable "buffer_interval" {
  type        = number
  description = "Buffer interval in seconds before flushing to OpenSearch"
  default     = 300

  validation {
    condition     = var.buffer_interval >= 60 && var.buffer_interval <= 900
    error_message = "Buffer interval must be between 60 and 900 seconds"
  }
}

variable "retry_duration" {
  type        = number
  description = "Retry duration in seconds for failed records"
  default     = 300

  validation {
    condition     = var.retry_duration >= 0 && var.retry_duration <= 7200
    error_message = "Retry duration must be between 0 and 7200 seconds"
  }
}

#------------------------------------------------------------------------------
# Backup Configuration
#------------------------------------------------------------------------------

variable "backup_retention_days" {
  type        = number
  description = "Number of days to retain backup data in S3"
  default     = 30

  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention days must be between 1 and 365"
  }
}

#------------------------------------------------------------------------------
# Log Sources Configuration
#------------------------------------------------------------------------------

variable "enable_guardduty_subscription" {
  type        = bool
  description = "Enable subscription filter for GuardDuty logs"
  default     = false
}

variable "guardduty_log_group_name" {
  type        = string
  description = "CloudWatch log group name for GuardDuty findings"
  default     = ""
}

variable "enable_vpc_flow_subscription" {
  type        = bool
  description = "Enable subscription filter for VPC Flow Logs"
  default     = false
}

variable "vpc_flow_log_group_name" {
  type        = string
  description = "CloudWatch log group name for VPC Flow Logs"
  default     = ""
}

variable "enable_cloudtrail_subscription" {
  type        = bool
  description = "Enable subscription filter for CloudTrail logs"
  default     = false
}

variable "cloudtrail_log_group_name" {
  type        = string
  description = "CloudWatch log group name for CloudTrail logs"
  default     = ""
}

#------------------------------------------------------------------------------
# Monitoring Configuration
#------------------------------------------------------------------------------

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period"
  }
}

variable "alarm_actions" {
  type        = list(string)
  description = "SNS topic ARNs for CloudWatch alarms"
  default     = []
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  type        = map(string)
  description = "Additional tags for all resources"
  default     = {}
}
