##############################################################################
# RDS Module - main.tf
# Provisions a production-ready RDS instance with:
#   - DB subnet group
#   - Security group (ingress from app SGs)
#   - Parameter group (MySQL or PostgreSQL)
#   - Random password stored in AWS Secrets Manager
#   - CloudWatch alarms for CPU, storage, and connections
##############################################################################

##############################################################################
# Random password
##############################################################################

resource "random_password" "db" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
  min_special      = 2
}

##############################################################################
# Secrets Manager – store the generated password
##############################################################################

resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.identifier}/db-password"
  description             = "RDS master password for ${var.identifier}"
  recovery_window_in_days = 7

  tags = merge(var.tags, {
    Name = "${var.identifier}-db-password"
  })
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = var.username
    password = random_password.db.result
    engine   = var.engine
    host     = aws_db_instance.this.address
    port     = aws_db_instance.this.port
    dbname   = var.db_name
  })

  # Wait until the DB is available before writing the host
  depends_on = [aws_db_instance.this]
}

##############################################################################
# DB Subnet Group
##############################################################################

resource "aws_db_subnet_group" "this" {
  name        = "${var.identifier}-subnet-group"
  description = "Subnet group for ${var.identifier} RDS instance"
  subnet_ids  = var.subnet_ids

  tags = merge(var.tags, {
    Name = "${var.identifier}-subnet-group"
  })
}

##############################################################################
# Security Group
##############################################################################

resource "aws_security_group" "rds" {
  name        = "${var.identifier}-rds-sg"
  description = "Security group for ${var.identifier} RDS instance"
  vpc_id      = var.vpc_id

  tags = merge(var.tags, {
    Name = "${var.identifier}-rds-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Ingress rules – one rule per source security group
resource "aws_security_group_rule" "rds_ingress" {
  for_each = toset(var.app_security_group_ids)

  type                     = "ingress"
  from_port                = local.db_port
  to_port                  = local.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = each.value
  description              = "Allow DB traffic from app SG ${each.value}"
}

# Egress – allow all outbound (required for AWS internal endpoints)
resource "aws_security_group_rule" "rds_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.rds.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow all outbound traffic"
}

##############################################################################
# Parameter Group
##############################################################################

resource "aws_db_parameter_group" "this" {
  name        = "${var.identifier}-params"
  family      = local.parameter_group_family
  description = "Parameter group for ${var.identifier} (${var.engine} ${var.engine_version})"

  dynamic "parameter" {
    for_each = local.db_parameters
    content {
      name         = parameter.value.name
      value        = parameter.value.value
      apply_method = lookup(parameter.value, "apply_method", "immediate")
    }
  }

  tags = merge(var.tags, {
    Name = "${var.identifier}-params"
  })

  lifecycle {
    create_before_destroy = true
  }
}

##############################################################################
# RDS Instance
##############################################################################

resource "aws_db_instance" "this" {
  identifier = var.identifier

  # Engine
  engine         = var.engine
  engine_version = var.engine_version

  # Compute and storage
  instance_class        = var.instance_class
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  # Credentials
  db_name  = var.db_name
  username = var.username
  password = random_password.db.result

  # Network
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # Parameter group
  parameter_group_name = aws_db_parameter_group.this.name

  # High availability
  multi_az = var.multi_az

  # Backup
  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window
  maintenance_window      = var.maintenance_window

  # Protection
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.identifier}-final-snapshot-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  # Monitoring
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_enhanced_monitoring.arn
  enabled_cloudwatch_logs_exports = local.cloudwatch_log_exports
  performance_insights_enabled    = true
  performance_insights_retention_period = 7

  # Auto minor version upgrades
  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true

  tags = merge(var.tags, {
    Name = var.identifier
  })

  depends_on = [
    aws_db_subnet_group.this,
    aws_db_parameter_group.this,
    aws_security_group.rds,
  ]
}

##############################################################################
# IAM Role for Enhanced Monitoring
##############################################################################

data "aws_iam_policy_document" "rds_enhanced_monitoring_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "rds_enhanced_monitoring" {
  name               = "${var.identifier}-rds-monitoring-role"
  assume_role_policy = data.aws_iam_policy_document.rds_enhanced_monitoring_assume.json

  tags = merge(var.tags, {
    Name = "${var.identifier}-rds-monitoring-role"
  })
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

##############################################################################
# CloudWatch Alarms
##############################################################################

resource "aws_cloudwatch_metric_alarm" "cpu_utilization" {
  alarm_name          = "${var.identifier}-rds-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization exceeded 80% for ${var.identifier}"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.this.identifier
  }

  tags = merge(var.tags, {
    Name = "${var.identifier}-rds-cpu-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "free_storage_space" {
  alarm_name          = "${var.identifier}-rds-free-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  # Alert when less than 10% of allocated storage remains (in bytes)
  threshold          = var.allocated_storage * 1073741824 * 0.10
  alarm_description  = "RDS free storage space below 10% for ${var.identifier}"
  treat_missing_data = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.this.identifier
  }

  tags = merge(var.tags, {
    Name = "${var.identifier}-rds-storage-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "${var.identifier}-rds-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = local.max_connections_threshold
  alarm_description   = "RDS connection count exceeded threshold for ${var.identifier}"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.this.identifier
  }

  tags = merge(var.tags, {
    Name = "${var.identifier}-rds-connections-alarm"
  })
}

##############################################################################
# Locals
##############################################################################

locals {
  # Derive port from engine
  db_port = var.engine == "mysql" || var.engine == "mariadb" ? 3306 : 5432

  # Parameter group family – map engine to family string
  parameter_group_family = (
    var.engine == "mysql"    ? "mysql${join(".", slice(split(".", var.engine_version), 0, 1))}" :
    var.engine == "mariadb"  ? "mariadb${join(".", slice(split(".", var.engine_version), 0, 2))}" :
    var.engine == "postgres" ? "postgres${split(".", var.engine_version)[0]}" :
    "${var.engine}${split(".", var.engine_version)[0]}"
  )

  # Engine-specific parameters
  db_parameters = var.engine == "postgres" ? [
    { name = "log_connections",        value = "1" },
    { name = "log_disconnections",     value = "1" },
    { name = "log_duration",           value = "0" },
    { name = "log_lock_waits",         value = "1" },
    { name = "log_min_duration_statement", value = "1000" },
    { name = "shared_preload_libraries",   value = "pg_stat_statements", apply_method = "pending-reboot" },
  ] : var.engine == "mysql" ? [
    { name = "slow_query_log",         value = "1" },
    { name = "long_query_time",        value = "1" },
    { name = "log_output",             value = "FILE" },
    { name = "general_log",            value = "0" },
    { name = "max_allowed_packet",     value = "67108864" },
    { name = "innodb_buffer_pool_size", value = "{DBInstanceClassMemory*3/4}", apply_method = "pending-reboot" },
  ] : []

  # CloudWatch log exports per engine
  cloudwatch_log_exports = var.engine == "postgres" ? ["postgresql", "upgrade"] : (
    var.engine == "mysql" ? ["error", "slowquery", "general"] : ["error"]
  )

  # Conservative connection threshold (80% of typical max)
  max_connections_map = {
    "db.t3.micro"   = 80
    "db.t3.small"   = 170
    "db.t3.medium"  = 340
    "db.t3.large"   = 680
    "db.r6g.large"  = 1360
    "db.r6g.xlarge" = 2730
  }
  max_connections_threshold = lookup(local.max_connections_map, var.instance_class, 100)
}
