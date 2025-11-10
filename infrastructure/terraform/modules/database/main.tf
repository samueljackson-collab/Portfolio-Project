variable "project_name" {
  type        = string
  description = "Project identifier"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID that hosts the database"
}

variable "db_username" {
  type        = string
  description = "Master database username"
}

variable "db_password" {
  type        = string
  description = "Master database password"
  sensitive   = true
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for the database subnet group"
}

variable "allowed_security_group_ids" {
  type        = list(string)
  description = "Security groups permitted to reach the database"
  default     = []
}

variable "instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t3.small"
}

variable "allocated_storage" {
  type        = number
  description = "Allocated storage in GiB"
  default     = 20
}

variable "max_allocated_storage" {
  type        = number
  description = "Maximum autoscaled storage in GiB"
  default     = 100
}

variable "engine_version" {
  type        = string
  description = "PostgreSQL engine version"
  default     = "15.4"
}

variable "multi_az" {
  type        = bool
  description = "Deploy database in multiple availability zones"
  default     = true
}

variable "backup_retention_period" {
  type        = number
  description = "Retention period for automated backups"
  default     = 7
}

variable "deletion_protection" {
  type        = bool
  description = "Enable deletion protection"
  default     = false
}

# NEW: control final snapshot behavior (safe default: do not skip final snapshot)
variable "skip_final_snapshot" {
  type        = bool
  description = "When true, skip creating a final snapshot on DB destroy. Defaults to false to protect data."
  default     = false
}

# NEW: allow apply_immediately to be configurable (default preserved)
variable "apply_immediately" {
  type        = bool
  description = "Control whether certain DB changes are applied immediately."
  default     = true
}

variable "performance_insights_enabled" {
  type        = bool
  description = "Enable Amazon RDS Performance Insights for the instance"
  default     = true
}

variable "performance_insights_retention_period" {
  type        = number
  description = "Retention period (in days) for Performance Insights metrics"
  default     = 7

  validation {
    condition     = contains([7, 731], var.performance_insights_retention_period)
    error_message = "performance_insights_retention_period must be either 7 or 731 days"
  }
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}

locals {
  name_prefix      = lower("${var.project_name}-${var.environment}")
  sanitized_prefix = replace(local.name_prefix, "_", "-")

  common_tags = merge({
    Project     = var.project_name
    Environment = var.environment
  }, var.tags)
}

resource "aws_security_group" "db" {
  name        = "${local.sanitized_prefix}-db-sg"
  description = "Database access rules"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.allowed_security_group_ids

    content {
      description     = "Allow Postgres from application security group"
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [ingress.value]
    }
  }

  egress {
    description = "Allow outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-sg"
  })
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.sanitized_prefix}-db-subnets"
  subnet_ids = var.subnet_ids

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnets"
  })
}

resource "aws_db_instance" "this" {
  identifier              = replace("${local.name_prefix}-db", "_", "-")
  engine                  = "postgres"
  engine_version          = var.engine_version
  instance_class          = var.instance_class
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  allocated_storage       = var.allocated_storage
  max_allocated_storage   = var.max_allocated_storage
  storage_encrypted       = true
  multi_az                = var.multi_az
  backup_retention_period = var.backup_retention_period
  auto_minor_version_upgrade = true
  deletion_protection        = var.deletion_protection

  # Use the configured variables for snapshot and apply behavior (safer defaults)
  skip_final_snapshot = var.skip_final_snapshot
  apply_immediately   = var.apply_immediately
  performance_insights_enabled           = var.performance_insights_enabled
  performance_insights_retention_period  = var.performance_insights_enabled ? var.performance_insights_retention_period : null

  publicly_accessible = false
  port                = 5432

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db"
  })
}

output "db_endpoint" {
  value = aws_db_instance.this.address
}

output "db_security_group_id" {
  value = aws_security_group.db.id
}

output "db_instance_arn" {
  value = aws_db_instance.this.arn
}
