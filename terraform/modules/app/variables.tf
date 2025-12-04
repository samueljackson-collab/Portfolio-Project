variable "project_tag" {
  description = "Project tag used for names and tagging"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR of the VPC for security group rules"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnets for database and application components"
  type        = list(string)
}

variable "create_rds" {
  description = "Create a PostgreSQL RDS instance"
  type        = bool
  default     = true
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database admin username"
  type        = string
}

variable "db_password" {
  description = "Database password (auto-generated if empty)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "Storage allocated to the database"
  type        = number
}

variable "db_instance_class" {
  description = "Instance class"
  type        = string
}

variable "db_engine_version" {
  description = "PostgreSQL version"
  type        = string
}

variable "db_backup_retention" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

variable "assets_bucket_name" {
  description = "Optional override for the assets bucket name"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
