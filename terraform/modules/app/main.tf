locals {
  bucket_suffix = random_id.bucket_suffix.hex
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "assets" {
  bucket = "${var.asset_bucket_prefix}-${local.bucket_suffix}"

  tags = merge(var.tags, {
    Name        = "${var.project_tag}-assets"
    Environment = var.environment
  })
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

resource "aws_security_group" "rds" {
  count = var.create_rds ? 1 : 0

  name        = "${var.project_tag}-rds-sg"
  description = "Allow DB access from VPC"
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

  tags = merge(var.tags, { Name = "${var.project_tag}-rds-sg" })
}

resource "aws_db_subnet_group" "this" {
  count = var.create_rds ? 1 : 0

  name       = "${var.project_tag}-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, { Name = "${var.project_tag}-rds-subnet-group" })
}

resource "random_password" "db" {
  count = var.create_rds && var.db_password == "" ? 1 : 0

  length  = 20
  special = true
}

resource "aws_db_instance" "postgres" {
  count = var.create_rds ? 1 : 0

  identifier              = "${var.project_tag}-db-${var.environment}"
  allocated_storage       = var.db_allocated_storage
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = var.db_instance_class
  name                    = var.db_name
  username                = var.db_username
  password                = var.db_password != "" ? var.db_password : random_password.db[0].result
  db_subnet_group_name    = aws_db_subnet_group.this[0].name
  vpc_security_group_ids  = [aws_security_group.rds[0].id]
  skip_final_snapshot     = var.skip_final_snapshot
  backup_retention_period = 7
  deletion_protection     = false
  publicly_accessible     = false

  tags = merge(var.tags, { Name = "${var.project_tag}-postgres" })
}

data "aws_iam_policy_document" "eks_assume_role" {
  count = var.enable_eks ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_cluster" {
  count = var.enable_eks ? 1 : 0

  name               = "${var.project_tag}-eks-cluster-${random_id.bucket_suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.eks_assume_role[0].json

  tags = merge(var.tags, { Name = "${var.project_tag}-eks-role" })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  count      = var.enable_eks ? 1 : 0
  role       = aws_iam_role.eks_cluster[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks_service_policy" {
  count      = var.enable_eks ? 1 : 0
  role       = aws_iam_role.eks_cluster[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
}

resource "aws_security_group" "eks" {
  count = var.enable_eks ? 1 : 0

  name        = "${var.project_tag}-eks-sg"
  description = "EKS cluster security group"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.project_tag}-eks-sg" })
}

resource "aws_eks_cluster" "this" {
  count    = var.enable_eks ? 1 : 0
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = var.eks_version

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.eks[0].id]
    endpoint_private_access = true
    endpoint_public_access  = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_service_policy
  ]
}
