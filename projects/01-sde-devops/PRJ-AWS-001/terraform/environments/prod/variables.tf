variable "project_name" { type = string }
variable "environment" { type = string }
variable "aws_region" { type = string }
variable "aws_profile" { type = string default = null }
variable "availability_zones" { type = list(string) }
variable "vpc_cidr" { type = string }
variable "common_tags" { type = map(string) default = {} }
variable "cost_center" { type = string default = "Engineering" }

variable "enable_nat_gateway" { type = bool default = true }
variable "single_nat_gateway" { type = bool default = false }
variable "enable_vpc_flow_logs" { type = bool default = true }
variable "flow_logs_retention_days" { type = number default = 30 }

variable "alb_ingress_cidrs" { type = list(string) default = ["0.0.0.0/0"] }
variable "bastion_cidrs" { type = list(string) default = [] }

variable "artifact_bucket_name" { type = string default = null }
variable "force_destroy_buckets" { type = bool default = false }
variable "kms_key_id" { type = string default = null }

variable "ami_id" { type = string }
variable "instance_type" { type = string default = "t3.medium" }
variable "ssh_key_name" { type = string default = null }
variable "iam_instance_profile" { type = string default = null }
variable "user_data_base64" { type = string default = null }
variable "desired_capacity" { type = number default = 2 }
variable "min_size" { type = number default = 2 }
variable "max_size" { type = number default = 4 }
variable "app_port" { type = number default = 8080 }
variable "health_check_path" { type = string default = "/healthz" }
variable "target_cpu_utilization" { type = number default = 50 }
variable "db_port" {
  description = "Port used by the database engine (propagates to security groups and NACL rules)"
  type        = number
  default     = 3306

  validation {
    condition     = var.db_port >= 1 && var.db_port <= 65535
    error_message = "Database port must be between 1 and 65535."
  }
}

variable "db_name" { type = string default = "appdb" }
variable "db_engine" { type = string default = "mysql" }
variable "db_engine_version" { type = string default = "8.0" }
variable "db_instance_class" { type = string default = "db.t4g.medium" }
variable "db_allocated_storage" { type = number default = 50 }
variable "db_max_allocated_storage" { type = number default = 200 }
variable "db_backup_retention_days" { type = number default = 7 }
variable "db_deletion_protection" { type = bool default = true }
variable "db_username" { type = string }
variable "db_password" { type = string sensitive = true }
variable "db_multi_az" { type = bool default = true }
variable "db_performance_insights" { type = bool default = true }

variable "alarm_sns_topic_arn" { type = string default = null }
