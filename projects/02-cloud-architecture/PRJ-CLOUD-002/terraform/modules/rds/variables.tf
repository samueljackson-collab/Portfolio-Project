variable "project_name" {
  description = "Project name for tagging."
  type        = string
}

variable "environment" {
  description = "Environment name for tagging."
  type        = string
}

variable "subnet_ids" {
  description = "Database subnet IDs across multiple availability zones."
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group protecting the database instance."
  type        = string
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
}

variable "allocated_storage" {
  description = "Initial storage allocated to the database (GB)."
  type        = number
}

variable "max_allocated_storage" {
  description = "Maximum storage RDS can scale to automatically (GB)."
  type        = number
}

variable "db_name" {
  description = "Name of the application database."
  type        = string
}

variable "db_username" {
  description = "Master username for the database."
  type        = string
}

variable "db_password" {
  description = "Optional master password. Leave blank to generate."
  type        = string
  default     = ""
  sensitive   = true
}

variable "multi_az" {
  description = "Whether to deploy the database across multiple availability zones."
  type        = bool
}

variable "backup_retention_days" {
  description = "Retention period for automated backups."
  type        = number
}

variable "enable_performance_insights" {
  description = "Enable Amazon RDS Performance Insights."
  type        = bool
}

variable "deletion_protection" {
  description = "Protect the database from accidental deletion."
  type        = bool
}

variable "tags" {
  description = "Common tags applied to RDS resources."
  type        = map(string)
  default     = {}
}
