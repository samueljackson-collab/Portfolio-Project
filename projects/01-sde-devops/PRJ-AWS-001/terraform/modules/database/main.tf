locals {
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Tier        = "database"
    }
  )
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnets"
  subnet_ids = var.private_db_subnet_ids

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-db-subnets" })
}

resource "aws_db_instance" "main" {
  identifier                = "${var.project_name}-${var.environment}-db"
  allocated_storage         = var.allocated_storage
  max_allocated_storage     = var.max_allocated_storage
  engine                    = var.db_engine
  engine_version            = var.db_engine_version
  instance_class            = var.instance_class
  db_subnet_group_name      = aws_db_subnet_group.main.name
  multi_az                  = var.multi_az
  username                  = var.db_username
  password                  = var.db_password
  db_name                   = var.db_name
  storage_encrypted         = true
  kms_key_id                = var.kms_key_id
  backup_retention_period   = var.backup_retention_days
  delete_automated_backups  = false
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-${var.environment}-final"
  vpc_security_group_ids    = var.db_security_group_ids
  monitoring_interval       = 60
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_kms_key_id = var.performance_insights_enabled ? var.kms_key_id : null
  apply_immediately         = false
  auto_minor_version_upgrade = true

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-db" })
}
