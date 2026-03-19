##############################################################################
# RDS Module - variables.tf
##############################################################################

variable "identifier" {
  description = "Unique identifier for the RDS instance and associated resources (e.g. 'myapp-prod-db')."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,61}[a-z0-9]$", var.identifier))
    error_message = "Identifier must start with a letter, contain only lowercase letters, numbers, and hyphens, and be 2-63 characters long."
  }
}

variable "engine" {
  description = "Database engine type. Supported values: 'postgres', 'mysql', 'mariadb'."
  type        = string
  default     = "postgres"

  validation {
    condition     = contains(["postgres", "mysql", "mariadb"], var.engine)
    error_message = "Engine must be one of: postgres, mysql, mariadb."
  }
}

variable "engine_version" {
  description = "Database engine version (e.g. '15.4' for PostgreSQL, '8.0.35' for MySQL)."
  type        = string
  default     = "15.4"
}

variable "instance_class" {
  description = "RDS instance class (e.g. 'db.t3.micro', 'db.t3.small', 'db.r6g.large')."
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Initial allocated storage size in GB."
  type        = number
  default     = 20

  validation {
    condition     = var.allocated_storage >= 20 && var.allocated_storage <= 65536
    error_message = "Allocated storage must be between 20 and 65536 GB."
  }
}

variable "max_allocated_storage" {
  description = "Maximum storage size in GB for autoscaling. Set to 0 to disable autoscaling."
  type        = number
  default     = 100

  validation {
    condition     = var.max_allocated_storage == 0 || var.max_allocated_storage >= 20
    error_message = "max_allocated_storage must be 0 (disabled) or >= 20."
  }
}

variable "db_name" {
  description = "Name of the initial database to create. Leave empty to skip initial database creation."
  type        = string
  default     = ""
}

variable "username" {
  description = "Master username for the database. Cannot be 'admin', 'root', or other reserved names."
  type        = string
  default     = "dbadmin"

  validation {
    condition     = !contains(["admin", "root", "master", "superuser"], lower(var.username))
    error_message = "Username cannot be a reserved word (admin, root, master, superuser)."
  }
}

variable "vpc_id" {
  description = "ID of the VPC where the RDS instance will be deployed."
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the DB subnet group. Must include subnets in at least 2 AZs."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "At least 2 subnet IDs are required for high availability."
  }
}

variable "app_security_group_ids" {
  description = "List of security group IDs from application servers/ECS tasks that need DB access."
  type        = list(string)
  default     = []
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment for high availability. Recommended for production."
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups (0 to disable, max 35)."
  type        = number
  default     = 7

  validation {
    condition     = var.backup_retention_period >= 0 && var.backup_retention_period <= 35
    error_message = "Backup retention period must be between 0 and 35 days."
  }
}

variable "backup_window" {
  description = "Preferred daily backup window in UTC (format: 'hh:mm-hh:mm')."
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred weekly maintenance window (format: 'ddd:hh:mm-ddd:hh:mm')."
  type        = string
  default     = "mon:04:00-mon:05:00"
}

variable "deletion_protection" {
  description = "Enable deletion protection to prevent accidental instance termination."
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when the DB instance is deleted. Set to false for production."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Map of tags to apply to all created resources."
  type        = map(string)
  default     = {}
}
