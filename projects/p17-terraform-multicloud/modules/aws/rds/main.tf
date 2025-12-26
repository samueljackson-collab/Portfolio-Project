locals {
  tags = merge(var.tags, { Project = var.project_name, Environment = var.environment })
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = var.db_subnet_ids

  tags = merge(local.tags, { Name = "${var.project_name}-db-subnet" })
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.project_name}-db-params"
  family = var.parameter_group_family

  dynamic "parameter" {
    for_each = var.parameters
    content {
      name  = parameter.value.name
      value = parameter.value.value
    }
  }

  tags = merge(local.tags, { Name = "${var.project_name}-db-params" })
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-db-sg"
  description = "RDS security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = var.port
    to_port     = var.port
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${var.project_name}-db-sg" })
}

resource "random_password" "db" {
  length           = 24
  special          = true
  override_special = "!@#%^*-_"
}

resource "aws_secretsmanager_secret" "db" {
  name                    = "${var.project_name}/rds/master"
  kms_key_id              = var.secrets_manager_kms_key_id
  recovery_window_in_days = 7

  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id

  secret_string = jsonencode({
    username = var.username
    password = random_password.db.result
    engine   = var.engine
    port     = var.port
    database = var.db_name
  })
}

resource "aws_db_instance" "primary" {
  identifier              = "${var.project_name}-db"
  engine                  = var.engine
  engine_version          = var.engine_version
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage
  max_allocated_storage   = var.max_allocated_storage
  db_name                 = var.db_name
  username                = var.username
  password                = random_password.db.result
  port                    = var.port
  multi_az                = var.multi_az
  storage_encrypted       = var.storage_encrypted
  kms_key_id              = var.kms_key_id
  vpc_security_group_ids  = [aws_security_group.db.id]
  db_subnet_group_name    = aws_db_subnet_group.this.name
  parameter_group_name    = aws_db_parameter_group.this.name
  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window
  maintenance_window      = var.maintenance_window
  deletion_protection     = var.deletion_protection
  skip_final_snapshot     = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : var.final_snapshot_identifier
  apply_immediately         = var.apply_immediately

  tags = merge(local.tags, { Name = "${var.project_name}-db" })
}

resource "aws_db_instance" "replica" {
  count = var.read_replica_count

  identifier             = "${var.project_name}-db-replica-${count.index}"
  replicate_source_db    = aws_db_instance.primary.identifier
  instance_class         = var.replica_instance_class
  port                   = var.port
  publicly_accessible    = false
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db.id]
  apply_immediately      = var.apply_immediately

  tags = merge(local.tags, { Name = "${var.project_name}-db-replica-${count.index}" })
}
