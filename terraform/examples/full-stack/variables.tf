variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "portfolio-example"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "vpc_cidr" {
  type    = string
  default = "10.10.0.0/16"
}

variable "public_subnets" {
  type = list(object({
    cidr = string
    az   = string
  }))
  default = [
    { cidr = "10.10.1.0/24", az = "us-east-1a" },
    { cidr = "10.10.2.0/24", az = "us-east-1b" }
  ]
}

variable "private_subnets" {
  type = list(object({
    cidr = string
    az   = string
  }))
  default = [
    { cidr = "10.10.11.0/24", az = "us-east-1a" },
    { cidr = "10.10.12.0/24", az = "us-east-1b" }
  ]
}
