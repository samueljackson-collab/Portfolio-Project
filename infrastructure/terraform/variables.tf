variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "default"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnets" {
  description = "Map of public subnet definitions"
  type = map(object({
    cidr  = string
    az    = string
    order = string
  }))
}

variable "private_subnets" {
  description = "Map of private subnet definitions"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "api_public_cidrs" {
  description = "CIDRs allowed to access the cluster endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "eks_desired_nodes" {
  type    = number
  default = 3
}

variable "eks_min_nodes" {
  type    = number
  default = 2
}

variable "eks_max_nodes" {
  type    = number
  default = 6
}

variable "eks_instance_type" {
  type    = string
  default = "m6i.large"
}

variable "eks_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.29"
}

variable "db_master_username" {
  description = "Master username for Aurora"
  type        = string
  sensitive   = true
}

variable "db_master_password" {
  description = "Master password for Aurora"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  type    = string
  default = "db.r6g.large"
}

variable "kms_key_id" {
  description = "KMS key for encryption"
  type        = string
}
