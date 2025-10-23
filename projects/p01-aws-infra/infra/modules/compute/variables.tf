variable "name" {
  description = "Prefix for naming resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment (prod/staging/etc)"
  type        = string
}

variable "ami_id" {
  description = "AMI used by compute instances"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "root_block_device" {
  description = "Root block device configuration"
  type = object({
    device_name = string
    volume_size = number
    volume_type = string
  })
  default = {
    device_name = "/dev/xvda"
    volume_size = 20
    volume_type = "gp3"
  }
}

variable "ssm_instance_profile" {
  description = "IAM instance profile providing SSM access"
  type        = string
}

variable "user_data_template" {
  description = "Path to user data template file"
  type        = string
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "info"
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "Security group ID for ALB"
  type        = string
}

variable "compute_security_group_id" {
  description = "Security group ID for compute nodes"
  type        = string
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8080
}

variable "health_check_path" {
  description = "Path used for ALB health checks"
  type        = string
  default     = "/healthz"
}

variable "acm_certificate_arn" {
  description = "ARN of ACM certificate for HTTPS"
  type        = string
}

variable "alb_ssl_policy" {
  description = "SSL policy for ALB listener"
  type        = string
  default     = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

variable "min_size" {
  description = "Minimum size of the ASG"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum size of the ASG"
  type        = number
  default     = 6
}

variable "desired_capacity" {
  description = "Desired capacity of the ASG"
  type        = number
  default     = 3
}

variable "enable_deletion_protection" {
  description = "Whether deletion protection is enabled for ALB"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}

