variable "project" {
  description = "Project tag used for resource naming"
  type        = string
  default     = "portfolio-platform"
}

variable "environment" {
  description = "Environment name (dev/stage/prod)"
  type        = string
  default     = "dev"
}

variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "Secondary AWS region for DR"
  type        = string
  default     = "eu-west-1"
}

variable "primary_cidr" {
  description = "CIDR block for the primary VPC"
  type        = string
  default     = "10.10.0.0/16"
}

variable "secondary_cidr" {
  description = "CIDR block for the secondary VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "eks_role_arn" {
  description = "Pre-provisioned IAM role ARN that EKS control planes assume"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes control plane version"
  type        = string
  default     = "1.29"
}
