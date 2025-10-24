resource "aws_db_subnet_group" "portfolio" {
  name       = "${local.name_prefix}-db"
  subnet_ids = values(aws_subnet.private)[*].id

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-db-subnets"
  })
}

resource "aws_rds_cluster" "portfolio" {
  cluster_identifier      = "${local.name_prefix}-aurora"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  master_username         = var.db_master_username
  master_password         = var.db_master_password
  database_name           = "portfolio"
  backup_retention_period = 7
  preferred_backup_window = "06:00-07:00"
  preferred_maintenance_window = "Sun:07:00-Sun:08:00"
  db_subnet_group_name    = aws_db_subnet_group.portfolio.name
  storage_encrypted       = true
  kms_key_id              = var.kms_key_id

  vpc_security_group_ids = [aws_security_group.db.id]

  scaling_configuration {
    auto_pause               = false
    max_capacity             = 32
    min_capacity             = 4
    seconds_until_auto_pause = 0
  }

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-aurora"
  })
}

resource "aws_rds_cluster_instance" "portfolio" {
  count              = 2
  identifier         = "${local.name_prefix}-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.portfolio.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.portfolio.engine
  publicly_accessible = false
  db_subnet_group_name = aws_db_subnet_group.portfolio.name

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-aurora-${count.index}"
  })
}

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db"
  description = "Database access"
  vpc_id      = aws_vpc.portfolio.id

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

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-db-sg"
  })
}

resource "aws_s3_bucket" "evidence" {
  bucket = "${local.name_prefix}-evidence"

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-evidence"
  })
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_id
      sse_algorithm     = "aws:kms"
    }
  }
}
