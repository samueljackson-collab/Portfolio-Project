variable "project_name" {
  description = "Project name for tagging."
  type        = string
}

variable "environment" {
  description = "Environment name for tagging."
  type        = string
}

variable "subnet_ids" {
  description = "Private subnets where application instances are deployed."
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group applied to application instances."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for application servers."
  type        = string
}

variable "key_name" {
  description = "Optional SSH key pair for instances."
  type        = string
  default     = ""
}

variable "target_group_arns" {
  description = "List of target group ARNs to register the Auto Scaling group with."
  type        = list(string)
}

variable "min_size" {
  description = "Minimum number of instances."
  type        = number
}

variable "desired_capacity" {
  description = "Desired number of instances."
  type        = number
}

variable "max_size" {
  description = "Maximum number of instances."
  type        = number
}

variable "app_port" {
  description = "Application port exposed on each instance."
  type        = number
}

variable "user_data" {
  description = "Optional custom user data script."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags applied to created resources."
  type        = map(string)
  default     = {}
}
