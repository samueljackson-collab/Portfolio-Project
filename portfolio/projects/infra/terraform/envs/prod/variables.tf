variable "aws_region" {
  description = "AWS region for infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "name" {
  description = "Prefix for environment resources"
  type        = string
  default     = "portfolio-prod"
}
