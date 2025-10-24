variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Friendly project identifier used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging and resource suffixes"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to spread the network across"
  type        = number
  default     = 2
}

variable "alb_allowed_cidrs" {
  description = "List of CIDR blocks allowed to reach the application load balancer"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "create_nat_gateways" {
  description = "When true, creates one NAT gateway per public subnet to provide outbound internet access for private subnets"
  type        = bool
  default     = true
}

variable "instance_type" {
  description = "EC2 instance type for the application auto scaling group"
  type        = string
  default     = "t3.micro"
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in the auto scaling group"
  type        = number
  default     = 2
}

variable "asg_min_size" {
  description = "Minimum number of instances in the auto scaling group"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum number of instances in the auto scaling group"
  type        = number
  default     = 4
}

variable "ami_id" {
  description = "Optional AMI ID override for the application instances"
  type        = string
  default     = ""
}

variable "db_username" {
  description = "Database master username"
  type        = string
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  description = "Initial storage allocation (GiB) for the database"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage (GiB) for autoscaling storage"
  type        = number
  default     = 100
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for the database"
  type        = bool
  default     = true
}

variable "db_backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "db_deletion_protection" {
  description = "Enable deletion protection on the RDS instance"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags applied to every supported resource"
  type        = map(string)
  default     = {}
}
