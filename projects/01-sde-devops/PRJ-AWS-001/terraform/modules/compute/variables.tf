variable "project_name" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_app_subnet_ids" { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "app_security_group_id" { type = string }
variable "common_tags" { type = map(string) default = {} }

variable "ami_id" { type = string }
variable "instance_type" { type = string default = "t3.micro" }
variable "ssh_key_name" { type = string default = null }
variable "iam_instance_profile" { type = string default = null }
variable "user_data_base64" { type = string default = null }
variable "create_instance_profile" { type = bool default = true }
variable "cloudwatch_log_group_name" { type = string default = null }
variable "cloudwatch_log_retention_days" { type = number default = 30 }
variable "app_log_path" { type = string default = "/var/log/app/app.log" }
variable "root_volume_size" { type = number default = 30 }
variable "root_volume_type" { type = string default = "gp3" }
variable "root_volume_device" { type = string default = "/dev/xvda" }
variable "enable_detailed_monitoring" { type = bool default = true }

variable "desired_capacity" { type = number default = 2 }
variable "min_size" { type = number default = 2 }
variable "max_size" { type = number default = 4 }
variable "app_port" { type = number default = 8080 }
variable "health_check_path" { type = string default = "/healthz" }
variable "target_cpu_utilization" { type = number default = 50 }
