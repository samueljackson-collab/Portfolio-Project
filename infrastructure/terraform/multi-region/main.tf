terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.62"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.primary_region
  alias  = "primary"
}

provider "aws" {
  region = var.secondary_region
  alias  = "secondary"
}

locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Networking per region
# -----------------------------------------------------------------------------
data "aws_availability_zones" "primary" {
  provider = aws.primary
  state    = "available"
}

data "aws_availability_zones" "secondary" {
  provider = aws.secondary
  state    = "available"
}

resource "aws_vpc" "primary" {
  provider             = aws.primary
  cidr_block           = var.primary_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(local.common_tags, { Name = "${var.project}-primary-vpc" })
}

resource "aws_vpc" "secondary" {
  provider             = aws.secondary
  cidr_block           = var.secondary_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(local.common_tags, { Name = "${var.project}-secondary-vpc" })
}

resource "aws_subnet" "primary_private" {
  provider          = aws.primary
  count             = 3
  vpc_id            = aws_vpc.primary.id
  cidr_block        = cidrsubnet(var.primary_cidr, 4, count.index)
  availability_zone = data.aws_availability_zones.primary.names[count.index]
  map_public_ip_on_launch = false
  tags = merge(local.common_tags, {
    Name   = "${var.project}-primary-private-${count.index}"
    Region = var.primary_region
    Tier   = "private"
  })
}

resource "aws_subnet" "secondary_private" {
  provider          = aws.secondary
  count             = 3
  vpc_id            = aws_vpc.secondary.id
  cidr_block        = cidrsubnet(var.secondary_cidr, 4, count.index)
  availability_zone = data.aws_availability_zones.secondary.names[count.index]
  map_public_ip_on_launch = false
  tags = merge(local.common_tags, {
    Name   = "${var.project}-secondary-private-${count.index}"
    Region = var.secondary_region
    Tier   = "private"
  })
}

# -----------------------------------------------------------------------------
# S3 multi-region replication for artifacts
# -----------------------------------------------------------------------------
resource "random_id" "replication_suffix" {
  byte_length = 3
}

data "aws_iam_policy_document" "replication" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "replication" {
  provider           = aws.primary
  name               = "${var.project}-${var.environment}-replication-${random_id.replication_suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.replication.json
}

data "aws_iam_policy_document" "replication_policy" {
  statement {
    sid    = "PrimaryBucketAccess"
    effect = "Allow"
    actions = [
      "s3:GetObjectVersionForReplication",
      "s3:GetObjectVersionAcl",
      "s3:GetObjectVersionTagging",
      "s3:ListBucket",
      "s3:GetReplicationConfiguration"
    ]
    resources = [aws_s3_bucket.primary.arn, "${aws_s3_bucket.primary.arn}/*"]
  }

  statement {
    sid     = "SecondaryWrite"
    effect  = "Allow"
    actions = ["s3:ReplicateObject", "s3:ReplicateDelete", "s3:ReplicateTags", "s3:GetObjectVersionTagging"]
    resources = [aws_s3_bucket.secondary.arn, "${aws_s3_bucket.secondary.arn}/*"]
  }
}

resource "aws_iam_role_policy" "replication" {
  provider = aws.primary
  name     = "${var.project}-${var.environment}-replication-policy"
  role     = aws_iam_role.replication.id
  policy   = data.aws_iam_policy_document.replication_policy.json
}

resource "aws_s3_bucket" "primary" {
  provider      = aws.primary
  bucket        = "${var.project}-${var.environment}-artifacts-${random_id.replication_suffix.hex}"
  force_destroy = true
  tags          = merge(local.common_tags, { Name = "primary-artifacts" })
}

resource "aws_s3_bucket_versioning" "primary" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket" "secondary" {
  provider      = aws.secondary
  bucket        = "${var.project}-${var.environment}-artifacts-dr-${random_id.replication_suffix.hex}"
  force_destroy = true
  tags          = merge(local.common_tags, { Name = "secondary-artifacts" })
}

resource "aws_s3_bucket_versioning" "secondary" {
  provider = aws.secondary
  bucket   = aws_s3_bucket.secondary.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_replication_configuration" "primary" {
  provider   = aws.primary
  bucket     = aws_s3_bucket.primary.id
  role       = aws_iam_role.replication.arn
  depends_on = [aws_s3_bucket_versioning.primary, aws_s3_bucket_versioning.secondary]

  rule {
    id     = "replicate-all"
    status = "Enabled"
    destination { bucket = aws_s3_bucket.secondary.arn }
  }
}

# -----------------------------------------------------------------------------
# DynamoDB Global Table for configuration
# -----------------------------------------------------------------------------
resource "aws_dynamodb_table" "service_config" {
  provider     = aws.primary
  name         = "${var.project}-${var.environment}-config"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "service"
  range_key    = "key"

  attribute { name = "service" type = "S" }
  attribute { name = "key" type = "S" }

  replica { region_name = var.secondary_region }

  tags = merge(local.common_tags, { Name = "service-config" })
}

# -----------------------------------------------------------------------------
# EKS control plane placeholders per region (GitOps driven)
# -----------------------------------------------------------------------------
resource "aws_eks_cluster" "primary" {
  provider = aws.primary
  name     = "${var.project}-primary-${var.environment}"
  role_arn = var.eks_role_arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids = aws_subnet.primary_private[*].id
  }

  tags = merge(local.common_tags, { Name = "primary-eks" })
}

resource "aws_eks_cluster" "secondary" {
  provider = aws.secondary
  name     = "${var.project}-secondary-${var.environment}"
  role_arn = var.eks_role_arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids = aws_subnet.secondary_private[*].id
  }

  tags = merge(local.common_tags, { Name = "secondary-eks" })
}

output "artifact_buckets" {
  description = "Primary/secondary artifact buckets"
  value = {
    primary   = aws_s3_bucket.primary.bucket
    secondary = aws_s3_bucket.secondary.bucket
  }
}

output "eks_clusters" {
  description = "Regional EKS cluster names"
  value = {
    primary   = aws_eks_cluster.primary.name
    secondary = aws_eks_cluster.secondary.name
  }
}
