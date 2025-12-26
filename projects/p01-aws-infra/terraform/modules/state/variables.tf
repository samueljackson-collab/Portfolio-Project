variable "create" {
  description = "Whether to create state resources (set true for bootstrap runs)"
  type        = bool
  default     = false
}

variable "bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  type        = string
}

variable "versioning_enabled" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "force_destroy_bucket" {
  description = "Allow Terraform to delete the state bucket (use with caution)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to created resources"
  type        = map(string)
  default     = {}
}
