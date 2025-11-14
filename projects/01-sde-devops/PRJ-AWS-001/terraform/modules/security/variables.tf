variable "project_name" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "common_tags" { type = map(string) default = {} }
variable "alb_ingress_cidrs" {
  description = "CIDR blocks allowed to reach the ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "bastion_cidrs" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = []
}

variable "app_port" {
  description = "Application listener port"
  type        = number
  default     = 8080
}

variable "db_port" {
  description = "Database listener port"
  type        = number
  default     = 3306
}
