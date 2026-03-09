variable "environment" {
  description = "Deployment environment (dev, staging, production)."
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones used by the VPC."
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks."
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "database_subnet_cidrs" {
  description = "Database subnet CIDR blocks."
  type        = list(string)
  default     = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]
}

variable "app_instance_type" {
  description = "EC2 instance type for application Auto Scaling Group."
  type        = string
  default     = "t3.small"
}

variable "app_min_size" {
  description = "Minimum number of application instances."
  type        = number
  default     = 2
}

variable "app_max_size" {
  description = "Maximum number of application instances."
  type        = number
  default     = 6
}

variable "app_desired_capacity" {
  description = "Desired number of application instances."
  type        = number
  default     = 2
}

variable "static_site_bucket_name" {
  description = "Optional custom name for the static site bucket. Must be globally unique."
  type        = string
  default     = null
}

variable "cloudfront_price_class" {
  description = "CloudFront price class (e.g., PriceClass_100, PriceClass_200, PriceClass_All)."
  type        = string
  default     = "PriceClass_100"
}

variable "db_username" {
  description = "Master username for the PostgreSQL database."
  type        = string
}

variable "db_password" {
  description = "Master password for the PostgreSQL database."
  type        = string
  sensitive   = true
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS. Leave empty for HTTP only."
  type        = string
  default     = ""
}
