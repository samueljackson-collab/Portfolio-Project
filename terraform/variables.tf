variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "tfstate_bucket" {
  description = "S3 bucket name for terraform state"
  type        = string
  default     = "twisted-monk-terraform-state-REPLACE_ME"
}

variable "tfstate_lock_table" {
  description = "DynamoDB table for state locking"
  type        = string
  default     = "twisted-monk-terraform-locks"
}

variable "project_tag" {
  description = "Project tag for resources"
  type        = string
  default     = "twisted-monk"
}
