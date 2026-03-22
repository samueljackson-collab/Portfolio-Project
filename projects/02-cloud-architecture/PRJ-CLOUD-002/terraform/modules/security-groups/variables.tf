variable "project_name" {
  description = "Project name for tagging."
  type        = string
}

variable "environment" {
  description = "Environment name for tagging."
  type        = string
}

variable "vpc_id" {
  description = "Identifier of the VPC in which the security groups are created."
  type        = string
}

variable "alb_allowed_cidrs" {
  description = "CIDR blocks allowed to reach the load balancer."
  type        = list(string)
}

variable "app_port" {
  description = "Port that the application tier listens on."
  type        = number
}

variable "tags" {
  description = "Common tags applied to resources."
  type        = map(string)
  default     = {}
}
