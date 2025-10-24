variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Optional named AWS CLI profile to use. Leave blank to use environment credentials."
  type        = string
  default     = ""
}

variable "project_name" {
  description = "Short name that is used in resource tags and identifiers."
  type        = string
  default     = "aws-multi-tier"
}

variable "environment" {
  description = "Environment tag applied to resources (e.g., prod, staging)."
  type        = string
  default     = "prod"
}

variable "owner" {
  description = "Owner or contact for the infrastructure."
  type        = string
  default     = "sams-jackson"
}

variable "cidr_block" {
  description = "Primary CIDR range for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones used for the multi-AZ deployment."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets in each availability zone."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for application subnets in each availability zone."
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets in each availability zone."
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

variable "alb_allowed_cidrs" {
  description = "CIDR ranges permitted to reach the Application Load Balancer."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "certificate_arn" {
  description = "ARN of the ACM certificate to terminate TLS on the load balancer."
  type        = string
}

variable "app_port" {
  description = "Port that the application servers listen on."
  type        = number
  default     = 80
}

variable "app_health_check_path" {
  description = "HTTP path used by the load balancer to verify instance health."
  type        = string
  default     = "/health"
}

variable "instance_type" {
  description = "Instance type for application servers in the Auto Scaling group."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Optional EC2 key pair for emergency SSH access. Leave blank to disable."
  type        = string
  default     = ""
}

variable "asg_min_size" {
  description = "Minimum number of application instances to run."
  type        = number
  default     = 2
}

variable "asg_desired_capacity" {
  description = "Desired number of application instances."
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum number of application instances to allow during scaling events."
  type        = number
  default     = 6
}

variable "db_instance_class" {
  description = "Instance class for the PostgreSQL database."
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage (GB) for the database."
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage (GB) RDS can automatically scale to."
  type        = number
  default     = 100
}

variable "db_multi_az" {
  description = "Whether to deploy PostgreSQL with Multi-AZ high availability."
  type        = bool
  default     = true
}

variable "db_name" {
  description = "Application database name."
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Master username for the PostgreSQL database."
  type        = string
  default     = "dbadmin"
}

variable "db_password" {
  description = "Optional master password. Leave blank to generate one automatically."
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_backup_retention_days" {
  description = "Retention period in days for automated RDS backups."
  type        = number
  default     = 7
}

variable "enable_performance_insights" {
  description = "Whether to enable Amazon RDS Performance Insights."
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address that should receive CloudWatch alarm notifications."
  type        = string
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on critical resources like the ALB and RDS instance."
  type        = bool
  default     = false
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch Logs for Flow Logs and application diagnostics."
  type        = number
  default     = 30
}

variable "extra_tags" {
  description = "Additional resource tags to merge with the standard set."
  type        = map(string)
  default     = {}
}
