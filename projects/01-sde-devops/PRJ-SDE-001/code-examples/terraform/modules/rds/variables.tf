# terraform/modules/rds/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for RDS"
  type        = list(string)
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Name of the database"
  type        = string
  default     = "portfolio"
}

variable "master_username" {
  description = "Master username"
  type        = string
  default     = "dbadmin"
}

variable "create_replica" {
  description = "Whether to create read replica"
  type        = bool
  default     = false
}

variable "replica_instance_class" {
  description = "Instance class for replica"
  type        = string
  default     = "db.t3.small"
}

variable "allowed_security_groups" {
  description = "Security groups allowed to access database"
  type        = list(string)
  default     = []
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for alarms"
  type        = string
  default     = ""
}
