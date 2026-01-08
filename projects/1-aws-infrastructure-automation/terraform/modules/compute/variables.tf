###############################################################################
# Compute Module - Input Variables
###############################################################################

variable "name_prefix" {
  description = "Prefix for resource names (e.g., 'portfolio-dev')."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where resources will be created."
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the ASG instances."
  type        = list(string)
}

#------------------------------------------------------------------------------
# Instance Configuration
#------------------------------------------------------------------------------

variable "instance_type" {
  description = "EC2 instance type for the ASG."
  type        = string
  default     = "t3.small"
}

variable "ami_ssm_parameter" {
  description = "SSM parameter name for the AMI ID."
  type        = string
  default     = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
}

variable "app_port" {
  description = "Port the application listens on."
  type        = number
  default     = 80
}

variable "user_data" {
  description = "Custom user data script. Leave empty for default nginx setup."
  type        = string
  default     = ""
}

variable "cloudwatch_agent_config_ssm_parameter" {
  description = "SSM parameter path for CloudWatch Agent configuration."
  type        = string
  default     = "AmazonCloudWatch-linux"
}

variable "enable_detailed_monitoring" {
  description = "Enable detailed monitoring for EC2 instances."
  type        = bool
  default     = true
}

#------------------------------------------------------------------------------
# Auto Scaling Configuration
#------------------------------------------------------------------------------

variable "min_size" {
  description = "Minimum number of instances in the ASG."
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of instances in the ASG."
  type        = number
  default     = 6
}

variable "desired_capacity" {
  description = "Desired number of instances in the ASG."
  type        = number
  default     = 2
}

variable "health_check_grace_period" {
  description = "Time (seconds) after instance launch before health checks."
  type        = number
  default     = 60
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization percentage for auto scaling."
  type        = number
  default     = 70
}

variable "enable_request_based_scaling" {
  description = "Enable request count based auto scaling."
  type        = bool
  default     = true
}

variable "target_requests_per_instance" {
  description = "Target requests per instance per minute for scaling."
  type        = number
  default     = 1000
}

#------------------------------------------------------------------------------
# Load Balancer Configuration
#------------------------------------------------------------------------------

variable "health_check_path" {
  description = "Health check path for the ALB target group."
  type        = string
  default     = "/healthz"
}

variable "enable_stickiness" {
  description = "Enable sticky sessions on the target group."
  type        = bool
  default     = false
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for the ALB."
  type        = bool
  default     = false
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS listener. Leave empty for HTTP only."
  type        = string
  default     = ""
}

variable "alb_access_logs_bucket" {
  description = "S3 bucket name for ALB access logs. Leave empty to disable."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# Security Configuration
#------------------------------------------------------------------------------

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the ALB."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}
