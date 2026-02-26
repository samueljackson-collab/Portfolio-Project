variable "project_name" {
  description = "Project name prefix for resources."
  type        = string
  default     = "prj-sde-003"
}

variable "environment" {
  description = "Deployment environment identifier."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region to deploy resources."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the environment VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs_count" {
  description = "Number of AZs to span."
  type        = number
  default     = 3
}

variable "enable_nat_gateway" {
  description = "Toggle NAT gateway creation."
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Force a single NAT gateway for cost savings."
  type        = bool
  default     = true
}

variable "enable_nat_gateway_per_az" {
  description = "Create NAT gateway in each AZ when enabled."
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs."
  type        = bool
  default     = false
}

variable "flow_logs_retention_days" {
  description = "CloudWatch retention for flow logs."
  type        = number
  default     = 7
}

variable "enable_s3_endpoint" {
  description = "Enable S3 gateway endpoint."
  type        = bool
  default     = true
}

variable "enable_dynamodb_endpoint" {
  description = "Enable DynamoDB gateway endpoint."
  type        = bool
  default     = false
}

variable "enable_ecr_endpoints" {
  description = "Enable ECR interface endpoints."
  type        = bool
  default     = false
}

variable "enable_ssm_endpoints" {
  description = "Enable SSM interface endpoints."
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Default tags applied to all resources."
  type        = map(string)
  default = {
    Project     = "PRJ-SDE-003"
    Environment = "dev"
    Owner       = "platform-team"
    Terraform   = "true"
  }
}
