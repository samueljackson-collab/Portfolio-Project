locals {
  tags             = merge(var.tags, { Component = "app" })
  bucket_name      = var.assets_bucket_name != "" ? var.assets_bucket_name : "${var.project_tag}-app-assets-${random_id.assets_suffix.hex}"
  db_password_safe = var.create_rds ? (var.db_password != "" ? var.db_password : random_password.db_password[0].result) : var.db_password
}

resource "random_id" "assets_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "assets" {
  bucket        = local.bucket_name
  force_destroy = false
  tags          = merge(local.tags, { Name = "${var.project_tag}-assets" })
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/portfolio/${var.project_tag}/app"
  retention_in_days = 30
  tags              = merge(local.tags, { Name = "${var.project_tag}-app-logs" })
}

resource "random_password" "db_password" {
  count   = var.create_rds && var.db_password == "" ? 1 : 0
  length  = 20
  special = true
}

resource "aws_db_subnet_group" "this" {
  count = var.create_rds ? 1 : 0

  name       = "${var.project_tag}-db-subnets"
  subnet_ids = var.private_subnet_ids
  tags       = merge(local.tags, { Name = "${var.project_tag}-db-subnets" })
}

resource "aws_security_group" "db" {
  count = var.create_rds ? 1 : 0

  name        = "${var.project_tag}-db-sg"
  description = "Database access from VPC"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${var.project_tag}-db-sg" })
}

resource "aws_db_instance" "this" {
  count = var.create_rds ? 1 : 0

  identifier              = "${var.project_tag}-db-${terraform.workspace}"
  allocated_storage       = var.db_allocated_storage
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = var.db_instance_class
  name                    = var.db_name
  username                = var.db_username
  password                = local.db_password_safe
  db_subnet_group_name    = aws_db_subnet_group.this[0].name
  vpc_security_group_ids  = [aws_security_group.db[0].id]
  backup_retention_period = var.db_backup_retention
  skip_final_snapshot     = true
  apply_immediately       = true
  multi_az                = false

  tags = merge(local.tags, { Name = "${var.project_tag}-postgres" })
}
