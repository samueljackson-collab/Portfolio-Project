variable "project_name" {
  description = "Human friendly project name used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment identifier (e.g. dev, staging, prod)."
  type        = string
}

variable "region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR range for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to spread resources across."
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type for application servers."
  type        = string
  default     = "t3.micro"
}

variable "desired_capacity" {
  description = "Desired number of instances in the Auto Scaling Group."
  type        = number
  default     = 2
}

variable "db_instance_class" {
  description = "Instance class for the RDS database."
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB for the RDS instance."
  type        = number
  default     = 20
}

variable "db_master_username" {
  description = "Master username for the PostgreSQL database."
  type        = string
  default     = "app_user"
}

variable "db_master_password" {
  description = "Master password for the PostgreSQL database (stored securely)."
  type        = string
  sensitive   = true
}
