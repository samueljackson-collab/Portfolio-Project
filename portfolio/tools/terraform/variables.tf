variable "aws_region" {
  description = "AWS region for provisioning resources"
  type        = string
  default     = "us-east-1"
}

variable "frontend_bucket_name" {
  description = "S3 bucket for hosting the frontend"
  type        = string
  default     = "portfolio-frontend-sample"
}
