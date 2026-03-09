variable "project_name" { type = string }
variable "environment" { type = string }
variable "common_tags" { type = map(string) default = {} }
variable "private_db_subnet_ids" { type = list(string) }
variable "db_security_group_ids" { type = list(string) }
variable "db_name" { type = string default = "appdb" }
variable "db_engine" { type = string default = "mysql" }
variable "db_engine_version" { type = string default = "8.0" }
variable "instance_class" { type = string default = "db.t4g.medium" }
variable "allocated_storage" { type = number default = 50 }
variable "max_allocated_storage" { type = number default = 100 }
variable "backup_retention_days" { type = number default = 7 }
variable "deletion_protection" { type = bool default = true }
variable "db_username" { type = string }
variable "db_password" { type = string sensitive = true }
variable "multi_az" { type = bool default = true }
variable "kms_key_id" { type = string default = null }
variable "performance_insights_enabled" { type = bool default = true }
