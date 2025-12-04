resource "random_id" "bucket" {
  byte_length = 4
}

resource "aws_s3_bucket" "app" {
  bucket = "${var.project_name}-${var.environment}-assets-${random_id.bucket.hex}"

  force_destroy = var.app_bucket_force_destroy

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-assets"
  })
}

resource "aws_s3_bucket_public_access_block" "app" {
  bucket = aws_s3_bucket.app.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "app" {
  bucket = aws_s3_bucket.app.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app" {
  bucket = aws_s3_bucket.app.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_security_group" "rds" {
  count = var.create_rds ? 1 : 0

  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Database access"
  vpc_id      = var.vpc_id

  ingress {
    description = "VPC internal access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = concat([var.vpc_cidr], var.allowed_cidrs)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  })
}

resource "aws_db_subnet_group" "this" {
  count = var.create_rds ? 1 : 0

  name       = "${var.project_name}-${var.environment}-rds-subnets"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-rds-subnets"
  })
}

resource "random_password" "db" {
  count = var.create_rds && var.db_password == "" ? 1 : 0

  length  = 20
  special = true
}

resource "aws_db_instance" "postgres" {
  count = var.create_rds ? 1 : 0

  identifier              = "${var.project_name}-${var.environment}-db"
  allocated_storage       = var.db_allocated_storage
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = var.db_instance_class
  name                    = var.db_name
  username                = var.db_username
  password                = var.db_password != "" ? var.db_password : random_password.db[0].result
  db_subnet_group_name    = aws_db_subnet_group.this[0].name
  vpc_security_group_ids  = [aws_security_group.rds[0].id]
  skip_final_snapshot     = true
  deletion_protection     = false
  multi_az                = false
  storage_encrypted       = true
  auto_minor_version_upgrade = true
  publicly_accessible     = false
  backup_retention_period = 7

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-postgres"
  })
}
