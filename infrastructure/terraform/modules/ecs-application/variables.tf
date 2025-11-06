# ECS Application Module Variables

variable "project_name" {
  type        = string
  description = "Project identifier for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where resources will be created"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for the Application Load Balancer"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for ECS tasks"
}

# Container Configuration
variable "container_name" {
  type        = string
  description = "Name of the container"
  default     = "app"
}

variable "container_image" {
  type        = string
  description = "Docker image for the application (e.g., nginx:latest or ECR URI)"
}

variable "container_port" {
  type        = number
  description = "Port the container listens on"
  default     = 80
}

variable "environment_variables" {
  type = list(object({
    name  = string
    value = string
  }))
  description = "Environment variables for the container"
  default     = []
}

variable "container_health_check" {
  type = object({
    command     = list(string)
    interval    = number
    timeout     = number
    retries     = number
    startPeriod = number
  })
  description = "Container health check configuration"
  default = {
    command     = ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
    interval    = 30
    timeout     = 5
    retries     = 3
    startPeriod = 60
  }
}

# ECS Task Configuration
variable "task_cpu" {
  type        = string
  description = "CPU units for the task (256, 512, 1024, 2048, 4096)"
  default     = "256"

  validation {
    condition     = contains(["256", "512", "1024", "2048", "4096"], var.task_cpu)
    error_message = "Task CPU must be 256, 512, 1024, 2048, or 4096"
  }
}

variable "task_memory" {
  type        = string
  description = "Memory for the task in MB (512, 1024, 2048, 4096, 8192, 16384, 30720)"
  default     = "512"
}

variable "desired_count" {
  type        = number
  description = "Desired number of tasks"
  default     = 2

  validation {
    condition     = var.desired_count >= 0
    error_message = "Desired count must be >= 0"
  }
}

# Service Configuration
variable "max_percent" {
  type        = number
  description = "Maximum percentage of tasks allowed during deployment"
  default     = 200
}

variable "min_percent" {
  type        = number
  description = "Minimum percentage of tasks required during deployment"
  default     = 100
}

variable "enable_execute_command" {
  type        = bool
  description = "Enable ECS Exec for debugging"
  default     = false
}

# Load Balancer Configuration
variable "internal_alb" {
  type        = bool
  description = "Whether the ALB is internal (private) or internet-facing"
  default     = false
}

variable "enable_deletion_protection" {
  type        = bool
  description = "Enable deletion protection on the ALB"
  default     = false
}

# Health Check Configuration
variable "health_check_path" {
  type        = string
  description = "Health check path"
  default     = "/"
}

variable "health_check_healthy_threshold" {
  type        = number
  description = "Number of consecutive successful health checks"
  default     = 2
}

variable "health_check_unhealthy_threshold" {
  type        = number
  description = "Number of consecutive failed health checks"
  default     = 3
}

variable "health_check_timeout" {
  type        = number
  description = "Health check timeout in seconds"
  default     = 5
}

variable "health_check_interval" {
  type        = number
  description = "Health check interval in seconds"
  default     = 30
}

variable "health_check_matcher" {
  type        = string
  description = "HTTP status codes to consider healthy"
  default     = "200"
}

# Auto Scaling Configuration
variable "enable_autoscaling" {
  type        = bool
  description = "Enable auto scaling for ECS service"
  default     = true
}

variable "min_capacity" {
  type        = number
  description = "Minimum number of tasks for auto scaling"
  default     = 1
}

variable "max_capacity" {
  type        = number
  description = "Maximum number of tasks for auto scaling"
  default     = 10
}

variable "cpu_target_value" {
  type        = number
  description = "Target CPU utilization percentage for auto scaling"
  default     = 70
}

variable "memory_target_value" {
  type        = number
  description = "Target memory utilization percentage for auto scaling"
  default     = 80
}

# Capacity Provider Configuration
variable "fargate_base" {
  type        = number
  description = "Base number of tasks to run on FARGATE"
  default     = 1
}

variable "fargate_weight" {
  type        = number
  description = "Relative weight of FARGATE capacity provider"
  default     = 1
}

variable "enable_fargate_spot" {
  type        = bool
  description = "Enable FARGATE_SPOT capacity provider"
  default     = false
}

variable "fargate_spot_weight" {
  type        = number
  description = "Relative weight of FARGATE_SPOT capacity provider"
  default     = 1
}

# Logging Configuration
variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period"
  }
}

variable "enable_container_insights" {
  type        = bool
  description = "Enable Container Insights for enhanced monitoring"
  default     = true
}

# Database Configuration (optional)
variable "database_security_group_id" {
  type        = string
  description = "Security group ID of the database (for task permissions)"
  default     = ""
}

variable "tags" {
  type        = map(string)
  description = "Additional tags for all resources"
  default     = {}
}
