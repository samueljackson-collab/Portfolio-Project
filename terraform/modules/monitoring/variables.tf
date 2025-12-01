variable "project_tag" {
  description = "Project tag and naming prefix"
  type        = string
}

variable "log_group_names" {
  description = "CloudWatch log groups to retain"
  type        = list(string)
  default     = []
}

variable "rds_identifier" {
  description = "Optional RDS identifier to monitor"
  type        = string
  default     = null
}

variable "alarm_emails" {
  description = "Email addresses subscribed to alerts"
  type        = list(string)
  default     = []
}

variable "enable_rds_alarm" {
  description = "Enable CPU and storage alarms for RDS"
  type        = bool
  default     = true
}

variable "log_retention" {
  description = "Retention in days for created log groups"
  type        = number
  default     = 30
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
