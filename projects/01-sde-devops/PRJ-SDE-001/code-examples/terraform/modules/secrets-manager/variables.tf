# =====================================================
# AWS Secrets Manager Module - Variables
# =====================================================

variable "secret_name" {
  description = "Name of the secret (must be unique within the AWS account)"
  type        = string

  validation {
    condition     = length(var.secret_name) > 0 && length(var.secret_name) <= 512
    error_message = "Secret name must be between 1 and 512 characters."
  }
}

variable "description" {
  description = "Description of the secret"
  type        = string
  default     = "Managed by Terraform"
}

variable "environment" {
  description = "Environment name (dev, stage, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "Environment must be dev, stage, or prod."
  }
}

variable "secret_value" {
  description = "Secret value to store. If null, a random password will be generated."
  type        = string
  default     = null
  sensitive   = true
}

variable "password_length" {
  description = "Length of generated password if secret_value is not provided"
  type        = number
  default     = 32

  validation {
    condition     = var.password_length >= 16 && var.password_length <= 128
    error_message = "Password length must be between 16 and 128 characters."
  }
}

variable "kms_key_id" {
  description = "ARN or ID of the KMS key to encrypt the secret. If not provided, uses default encryption."
  type        = string
  default     = null
}

variable "recovery_window_in_days" {
  description = "Number of days to retain secret after deletion (7-30 days, or 0 for immediate deletion)"
  type        = number
  default     = 30

  validation {
    condition     = var.recovery_window_in_days == 0 || (var.recovery_window_in_days >= 7 && var.recovery_window_in_days <= 30)
    error_message = "Recovery window must be 0 (immediate deletion) or between 7 and 30 days."
  }
}

variable "enable_rotation" {
  description = "Enable automatic secret rotation"
  type        = bool
  default     = false
}

variable "rotation_days" {
  description = "Number of days between automatic rotations (only applies if enable_rotation is true)"
  type        = number
  default     = 90

  validation {
    condition     = var.rotation_days >= 1 && var.rotation_days <= 365
    error_message = "Rotation days must be between 1 and 365."
  }
}

variable "allowed_iam_arns" {
  description = "List of IAM role/user ARNs allowed to read the secret"
  type        = list(string)
  default     = []
}

variable "vpc_config" {
  description = "VPC configuration for rotation Lambda function (required if database is in VPC)"
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
