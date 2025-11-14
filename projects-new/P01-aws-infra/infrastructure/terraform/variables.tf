variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "AWS Infrastructure Automation"
}

variable "log_retention_days" {
  description = "Number of days to retain application logs"
  type        = number
  default     = 30
}

variable "api_key_value" {
  description = "API key stored in SSM for the FastAPI service"
  type        = string
  default     = "local-dev-key"
  sensitive   = true
}
