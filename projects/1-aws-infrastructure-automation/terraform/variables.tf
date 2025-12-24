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

variable "web_instance_type" {
  description = "Instance type for the web Auto Scaling Group."
  type        = string
  default     = "t3.micro"
}

variable "web_min_size" {
  description = "Minimum number of instances in the web Auto Scaling Group."
  type        = number
  default     = 2
}

variable "web_max_size" {
  description = "Maximum number of instances in the web Auto Scaling Group."
  type        = number
  default     = 6
}

variable "web_desired_capacity" {
  description = "Desired capacity for the web Auto Scaling Group."
  type        = number
  default     = 3
}

variable "asset_bucket_name" {
  description = "Name of the S3 bucket used for static assets."
  type        = string
  default     = "portfolio-static-assets-example"
}

variable "cloudfront_price_class" {
  description = "CloudFront price class to control edge location coverage."
  type        = string
  default     = "PriceClass_200"
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
