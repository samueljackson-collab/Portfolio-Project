variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "backend_image" {
  description = "Container image for the FastAPI backend"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "IAM role used by ECS to pull images and publish logs"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "IAM role for the backend task runtime"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "bucket_prefix" {
  description = "Prefix for the static site bucket"
  type        = string
  default     = "web-app-assessment"
}

variable "backend_allowed_cidrs" {
  description = "CIDR blocks permitted to reach the backend service"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "db_password_secret_arn" {
  description = "ARN of the AWS Secrets Manager secret containing the database password"
  type        = string
  default     = ""
}

variable "skip_final_snapshot" {
  description = "Whether to skip final snapshot on RDS deletion (true for dev/test, false for prod)"
  type        = bool
  default     = true
}
