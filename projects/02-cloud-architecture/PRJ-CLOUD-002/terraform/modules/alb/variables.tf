variable "name_prefix" {
  description = "Prefix used when naming ALB resources."
  type        = string
}

variable "vpc_id" {
  description = "VPC where the load balancer operates."
  type        = string
}

variable "public_subnet_ids" {
  description = "Subnets for the Application Load Balancer."
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group assigned to the ALB."
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate used for TLS termination."
  type        = string
}

variable "target_group_port" {
  description = "Port exposed by the target group."
  type        = number
}

variable "health_check_path" {
  description = "HTTP path for ALB health checks."
  type        = string
}

variable "enable_deletion_protection" {
  description = "Whether deletion protection is enabled for the ALB."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to ALB resources."
  type        = map(string)
  default     = {}
}
