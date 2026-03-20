##############################################################################
# Example: mysql/variables.tf
##############################################################################

variable "aws_region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "ID of the VPC where the RDS instance will be created."
  type        = string
  # Example: "vpc-0abc123def456789a"
}

variable "subnet_ids" {
  description = "List of private subnet IDs (minimum 2, in different AZs) for the DB subnet group."
  type        = list(string)
  # Example: ["subnet-0aaa111", "subnet-0bbb222"]
}

variable "app_security_group_ids" {
  description = "Security group IDs of the application servers or ECS tasks that connect to the DB."
  type        = list(string)
  default     = []
  # Example: ["sg-0app123456789"]
}
