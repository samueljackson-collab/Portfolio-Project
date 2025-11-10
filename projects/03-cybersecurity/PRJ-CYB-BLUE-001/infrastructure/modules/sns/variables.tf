# SNS Module Variables

variable "topic_name" {
  description = "Name of the SNS topic"
  type        = string
}

variable "display_name" {
  description = "Display name for the SNS topic"
  type        = string
  default     = "Security Alerts"
}

variable "kms_key_id" {
  description = "KMS key ID for SNS encryption"
  type        = string
  default     = null
}

variable "email_addresses" {
  description = "List of email addresses to subscribe to alerts"
  type        = list(string)
  default     = []
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alert notifications"
  type        = string
  default     = null
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
