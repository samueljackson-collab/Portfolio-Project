variable "project_name" {
  description = "Project name used for tagging."
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging."
  type        = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB used for CloudWatch metrics."
  type        = string
}

variable "target_group_arn_suffix" {
  description = "ARN suffix of the target group used for CloudWatch metrics."
  type        = string
}

variable "autoscaling_group_name" {
  description = "Name of the application Auto Scaling group."
  type        = string
}

variable "db_instance_id" {
  description = "Identifier of the RDS database instance."
  type        = string
}

variable "vpc_id" {
  description = "VPC identifier used for flow logs."
  type        = string
}

variable "alert_email" {
  description = "Email address that receives monitoring alerts."
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention for diagnostics."
  type        = number
}

variable "tags" {
  description = "Common tags applied to monitoring resources."
  type        = map(string)
  default     = {}
}
