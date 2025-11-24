variable "project" {
  description = "Base project tag"
  type        = string
  default     = "roaming-sim"
}

variable "owner" {
  description = "Tag owner"
  type        = string
  default     = "platform-team"
}

variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "Secondary AWS region for failover"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr_base" {
  description = "Base CIDR used to carve per-region networks"
  type        = string
  default     = "10.20.0.0/16"
}

variable "peer_cidr" {
  description = "CIDR allowed to push OTLP traffic (e.g., CI runner network)"
  type        = string
  default     = "10.0.0.0/8"
}
