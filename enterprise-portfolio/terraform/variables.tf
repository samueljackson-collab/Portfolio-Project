variable "aws_region" {
  description = "AWS region used for foundational services"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "network_cidr" {
  description = "Primary CIDR block for the core network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "security_frameworks" {
  description = "Compliance frameworks enforced"
  type        = list(string)
  default     = ["CIS", "NIST"]
}

variable "enable_tracing" {
  description = "Enable distributed tracing components"
  type        = bool
  default     = true
}

variable "kubernetes_version" {
  description = "Managed Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "node_pools" {
  description = "Node pool configuration"
  type = list(object({
    name = string
    size = number
    type = string
  }))
  default = [
    {
      name = "default"
      size = 2
      type = "m5.large"
    }
  ]
}

variable "default_tags" {
  description = "Default resource tags"
  type        = map(string)
  default = {
    Project     = "enterprise-portfolio"
    Environment = "dev"
  }
}
