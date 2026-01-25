variable "project_name" {
  description = "Project identifier used for naming."
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)."
  type        = string
}

variable "private_db_subnet_ids" {
  description = "Subnets for database placement."
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security groups to attach to the database."
  type        = list(string)
}
