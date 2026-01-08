###############################################################################
# Monitoring Module - Input Variables
###############################################################################

variable "name_prefix" {
  description = "Prefix for resource names (e.g., 'portfolio-dev')."
  type        = string
}

#------------------------------------------------------------------------------
# Alert Configuration
#------------------------------------------------------------------------------

variable "alert_email_addresses" {
  description = "List of email addresses for alarm notifications."
  type        = list(string)
  default     = []
}

variable "kms_key_id" {
  description = "KMS key ID for encrypting SNS topics and log groups."
  type        = string
  default     = null
}

#------------------------------------------------------------------------------
# Log Group Configuration
#------------------------------------------------------------------------------

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs."
  type        = number
  default     = 30
}

#------------------------------------------------------------------------------
# Resource Identifiers for Dashboard
#------------------------------------------------------------------------------

variable "alb_arn_suffix" {
  description = "ALB ARN suffix for CloudWatch metrics."
  type        = string
  default     = ""
}

variable "target_group_arn_suffix" {
  description = "Target group ARN suffix for CloudWatch metrics."
  type        = string
  default     = ""
}

variable "asg_name" {
  description = "Auto Scaling Group name for CloudWatch metrics."
  type        = string
  default     = ""
}

variable "rds_identifier" {
  description = "RDS instance identifier for CloudWatch metrics."
  type        = string
  default     = ""
}

variable "nat_gateway_id" {
  description = "NAT Gateway ID for CloudWatch metrics."
  type        = string
  default     = ""
}

variable "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for CloudWatch metrics."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# Alarm Configuration
#------------------------------------------------------------------------------

variable "create_alarms" {
  description = "Create CloudWatch alarms."
  type        = bool
  default     = true
}

variable "alb_5xx_threshold" {
  description = "Threshold for ALB 5xx error alarm."
  type        = number
  default     = 10
}

variable "alb_response_time_threshold" {
  description = "Threshold (seconds) for ALB response time alarm."
  type        = number
  default     = 2
}

variable "ec2_cpu_threshold" {
  description = "Threshold (percentage) for EC2 CPU alarm."
  type        = number
  default     = 80
}

variable "rds_cpu_threshold" {
  description = "Threshold (percentage) for RDS CPU alarm."
  type        = number
  default     = 80
}

variable "rds_storage_threshold" {
  description = "Threshold (bytes) for RDS free storage alarm."
  type        = number
  default     = 5368709120  # 5 GB
}

variable "rds_connections_threshold" {
  description = "Threshold for RDS connections alarm."
  type        = number
  default     = 80
}

variable "application_error_threshold" {
  description = "Threshold for application error count alarm."
  type        = number
  default     = 10
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}
