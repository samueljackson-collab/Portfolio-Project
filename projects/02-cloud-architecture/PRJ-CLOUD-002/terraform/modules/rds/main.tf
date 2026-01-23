resource "random_password" "master" {
  length  = 24
  special = true
  override_characters = "!#%^*()-_=+"
}

locals {
  db_identifier = "${var.project_name}-${var.environment}-db"
  db_password   = var.db_password != "" ? var.db_password : random_password.master.result
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.project_name}-${var.environment}-db-subnet"
  subnet_ids = var.subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db-subnets"
  })
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.project_name}-${var.environment}-pg"
  family = "postgres15"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_statement"
    value = "none"
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-pg"
  })
}

resource "aws_iam_role" "monitoring" {
  name_prefix = "${var.project_name}-${var.environment}-rds-monitor-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "monitoring" {
  role       = aws_iam_role.monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

resource "aws_db_instance" "this" {
  identifier = local.db_identifier

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.instance_class

  db_name  = var.db_name
  username = var.db_username
  password = local.db_password
  port     = 5432

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_encrypted     = true
  storage_type          = "gp3"

  multi_az               = var.multi_az
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [var.security_group_id]
  publicly_accessible    = false

  backup_retention_period = var.backup_retention_days
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.monitoring.arn

  performance_insights_enabled         = var.enable_performance_insights
  performance_insights_retention_period = var.enable_performance_insights ? 7 : null

  parameter_group_name = aws_db_parameter_group.this.name

  apply_immediately  = true
  deletion_protection      = var.deletion_protection
  skip_final_snapshot      = !var.deletion_protection
  final_snapshot_identifier = "${local.db_identifier}-final"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-postgres"
  })
}

resource "aws_secretsmanager_secret" "credentials" {
  name = "${var.project_name}-${var.environment}-db-credentials"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "credentials" {
  secret_id = aws_secretsmanager_secret.credentials.id

  secret_string = jsonencode({
    username = var.db_username
    password = local.db_password
    engine   = "postgres"
    host     = aws_db_instance.this.address
    port     = 5432
    dbname   = var.db_name
  })
}
