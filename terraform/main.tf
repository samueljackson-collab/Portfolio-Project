provider "aws" {
  region = var.aws_region
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  common_tags = {
    Project = var.project_tag
    Owner   = "samueljackson-collab"
    Env     = terraform.workspace
  }
}

# VPC
resource "aws_vpc" "twisted_monk" {
  cidr_block = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(local.common_tags, { Name = "${var.project_tag}-vpc" })
}

data "aws_availability_zones" "available" {}

# Public subnets
resource "aws_subnet" "public" {
  for_each = toset(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.twisted_monk.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
  tags = merge(local.common_tags, { Name = "${var.project_tag}-public-${each.key}" })
}

# Private subnets
resource "aws_subnet" "private" {
  for_each = toset(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.twisted_monk.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false
  tags = merge(local.common_tags, { Name = "${var.project_tag}-private-${each.key}" })
}

# Internet Gateway + Route Table
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.twisted_monk.id
  tags   = merge(local.common_tags, { Name = "${var.project_tag}-igw" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.twisted_monk.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = merge(local.common_tags, { Name = "${var.project_tag}-public-rt" })
}

resource "aws_route_table_association" "public_assocs" {
  for_each = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

# RDS Subnet Group and instance (optional)
resource "aws_db_subnet_group" "rds_subnets" {
  count = var.create_rds ? 1 : 0
  name       = "${var.project_tag}-rds-subnet-group"
  subnet_ids = values(aws_subnet.private)[*].id
  tags = merge(local.common_tags, { Name = "${var.project_tag}-rds-subnet-group" })
}

resource "random_password" "db" {
  count = var.create_rds && var.db_password == "" ? 1 : 0
  length           = 16
  special          = true
  override_characters = "@#%+=:;,-.[]{}()<>"
}

resource "aws_db_instance" "postgres" {
  count = var.create_rds ? 1 : 0
  identifier = "${var.project_tag}-db-${terraform.workspace}"
  allocated_storage    = var.db_allocated_storage
  engine               = "postgres"
  engine_version       = var.db_engine_version
  instance_class       = var.db_instance_class
  name                 = var.db_name
  username             = var.db_username
  password             = var.db_password != "" ? var.db_password : random_password.db[0].result
  db_subnet_group_name = aws_db_subnet_group.rds_subnets[0].name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot  = true
  tags = merge(local.common_tags, { Name = "${var.project_tag}-postgres" })
}

# RDS Security Group
resource "aws_security_group" "rds_sg" {
  name        = "${var.project_tag}-rds-sg"
  description = "Allow DB access from VPC"
  vpc_id      = aws_vpc.twisted_monk.id
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
  tags = merge(local.common_tags, { Name = "${var.project_tag}-rds-sg" })
}

# Optional EKS cluster (disabled by default)
resource "aws_iam_role" "eks_cluster_role" {
  count = var.create_eks ? 1 : 0
  name = "${var.project_tag}-eks-cluster-role-${random_id.bucket_suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.eks_assume_role[0].json
}

data "aws_iam_policy_document" "eks_assume_role" {
  count = var.create_eks ? 1 : 0
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_eks_cluster" "cluster" {
  count = var.create_eks ? 1 : 0
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.eks_cluster_role[0].arn

  vpc_config {
    subnet_ids = values(aws_subnet.private)[*].id
  }

  depends_on = [aws_iam_role.eks_cluster_role]
}

# S3 Bucket for application assets
resource "aws_s3_bucket" "app_assets" {
  bucket = "${var.project_tag}-assets-${random_id.bucket_suffix.hex}"
  tags   = merge(local.common_tags, { Name = "${var.project_tag}-assets" })
}

resource "aws_s3_bucket_public_access_block" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
