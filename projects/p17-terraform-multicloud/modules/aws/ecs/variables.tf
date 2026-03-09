variable "project_name" {
  description = "Name prefix for resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging."
  type        = string
}

variable "region" {
  description = "AWS region for log configuration."
  type        = string
}

variable "cluster_name" {
  description = "ECS cluster name."
  type        = string
  default     = "portfolio-cluster"
}

variable "vpc_id" {
  description = "VPC ID for ECS security group."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS service."
  type        = list(string)
}

variable "security_group_ids" {
  description = "Existing security group IDs. If empty, the module creates one."
  type        = list(string)
  default     = []
}

variable "service_ingress_cidrs" {
  description = "CIDR blocks allowed to access the service when module creates the security group."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "container_image" {
  description = "Container image to deploy."
  type        = string
}

variable "container_port" {
  description = "Container port exposed by the service."
  type        = number
  default     = 80
}

variable "cpu" {
  description = "Task CPU units."
  type        = string
  default     = "512"
}

variable "memory" {
  description = "Task memory in MiB."
  type        = string
  default     = "1024"
}

variable "desired_count" {
  description = "Desired task count."
  type        = number
  default     = 2
}

variable "assign_public_ip" {
  description = "Assign public IP to tasks."
  type        = bool
  default     = false
}

variable "execution_role_arn" {
  description = "IAM role ARN for ECS task execution."
  type        = string
  default     = null
}

variable "task_role_arn" {
  description = "IAM role ARN for the task."
  type        = string
  default     = null
}

variable "environment_variables" {
  description = "Map of environment variables for the container."
  type        = map(string)
  default     = {}
}

variable "load_balancer_target_group_arn" {
  description = "Target group ARN for an ALB."
  type        = string
  default     = null
}

variable "enable_autoscaling" {
  description = "Enable ECS service autoscaling."
  type        = bool
  default     = true
}

variable "autoscaling_min_capacity" {
  description = "Minimum desired tasks."
  type        = number
  default     = 2
}

variable "autoscaling_max_capacity" {
  description = "Maximum desired tasks."
  type        = number
  default     = 6
}

variable "autoscaling_target_cpu" {
  description = "Target CPU utilization for scaling."
  type        = number
  default     = 60
}

variable "log_retention_in_days" {
  description = "CloudWatch log retention."
  type        = number
  default     = 30
}

variable "tags" {
  description = "Additional tags to apply."
  type        = map(string)
  default     = {}
}
