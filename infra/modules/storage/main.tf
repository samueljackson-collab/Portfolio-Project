resource "aws_db_subnet_group" "this" {
  name       = "${var.project_name}-${var.environment}-db-subnets"
  subnet_ids = var.db_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db-subnets"
  })
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name = "${var.project_name}-${var.environment}-db-credentials"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db-secret"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id     = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.master_username
    password = var.master_password
  })
}

resource "aws_db_instance" "this" {
  identifier              = "${var.project_name}-${var.environment}-db"
  engine                  = "postgres"
  engine_version          = "15.5"
  instance_class          = var.db_instance_class
  allocated_storage       = var.allocated_storage
  storage_encrypted       = true
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [var.db_security_group_id]
  username                = var.master_username
  password                = var.master_password
  backup_retention_period = 7
  skip_final_snapshot     = false
  deletion_protection     = true
  multi_az                = true
  publicly_accessible     = false
  apply_immediately       = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db"
  })
}
