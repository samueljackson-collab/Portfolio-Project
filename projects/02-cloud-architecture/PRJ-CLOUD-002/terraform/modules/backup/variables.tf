variable "project_name" {
  description = "Project name for tagging."
  type        = string
}

variable "environment" {
  description = "Environment name for tagging."
  type        = string
}

variable "rds_instance_arn" {
  description = "ARN of the RDS instance to protect with AWS Backup."
  type        = string
}

variable "tags" {
  description = "Tags applied to backup resources."
  type        = map(string)
  default     = {}
}
