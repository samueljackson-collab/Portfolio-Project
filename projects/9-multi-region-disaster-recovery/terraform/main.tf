terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Primary Region (us-east-1)
provider "aws" {
  region = var.primary_region
  alias  = "primary"
}

# DR Region (us-west-2)
provider "aws" {
  region = var.dr_region
  alias  = "dr"
}

# Global Route53 resources (no region)
provider "aws" {
  region = "us-east-1"
  alias  = "global"
}

# ========================================
# VPC Configuration - Primary Region
# ========================================

module "vpc_primary" {
  source = "terraform-aws-modules/vpc/aws"
  providers = {
    aws = aws.primary
  }

  name = "${var.project_name}-vpc-primary"
  cidr = var.primary_vpc_cidr

  azs             = ["${var.primary_region}a", "${var.primary_region}b", "${var.primary_region}c"]
  private_subnets = [cidrsubnet(var.primary_vpc_cidr, 4, 0), cidrsubnet(var.primary_vpc_cidr, 4, 1), cidrsubnet(var.primary_vpc_cidr, 4, 2)]
  public_subnets  = [cidrsubnet(var.primary_vpc_cidr, 4, 3), cidrsubnet(var.primary_vpc_cidr, 4, 4), cidrsubnet(var.primary_vpc_cidr, 4, 5)]

  enable_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Environment = var.environment
    Region      = "primary"
    Terraform   = "true"
  }
}

# ========================================
# VPC Configuration - DR Region
# ========================================

module "vpc_dr" {
  source = "terraform-aws-modules/vpc/aws"
  providers = {
    aws = aws.dr
  }

  name = "${var.project_name}-vpc-dr"
  cidr = var.dr_vpc_cidr

  azs             = ["${var.dr_region}a", "${var.dr_region}b", "${var.dr_region}c"]
  private_subnets = [cidrsubnet(var.dr_vpc_cidr, 4, 0), cidrsubnet(var.dr_vpc_cidr, 4, 1), cidrsubnet(var.dr_vpc_cidr, 4, 2)]
  public_subnets  = [cidrsubnet(var.dr_vpc_cidr, 4, 3), cidrsubnet(var.dr_vpc_cidr, 4, 4), cidrsubnet(var.dr_vpc_cidr, 4, 5)]

  enable_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Environment = var.environment
    Region      = "dr"
    Terraform   = "true"
  }
}

# ========================================
# Application Load Balancers
# ========================================

resource "aws_lb" "primary" {
  provider = aws.primary

  name               = "${var.project_name}-alb-primary"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_primary.id]
  subnets            = module.vpc_primary.public_subnets

  enable_deletion_protection = var.environment == "production"
  enable_http2               = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name        = "${var.project_name}-alb-primary"
    Region      = "primary"
    Environment = var.environment
  }
}

resource "aws_lb" "dr" {
  provider = aws.dr

  name               = "${var.project_name}-alb-dr"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_dr.id]
  subnets            = module.vpc_dr.public_subnets

  enable_deletion_protection = var.environment == "production"
  enable_http2               = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name        = "${var.project_name}-alb-dr"
    Region      = "dr"
    Environment = var.environment
  }
}

# ========================================
# Security Groups
# ========================================

resource "aws_security_group" "alb_primary" {
  provider = aws.primary

  name        = "${var.project_name}-alb-sg-primary"
  description = "Security group for ALB in primary region"
  vpc_id      = module.vpc_primary.vpc_id

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-alb-sg-primary"
  }
}

resource "aws_security_group" "alb_dr" {
  provider = aws.dr

  name        = "${var.project_name}-alb-sg-dr"
  description = "Security group for ALB in DR region"
  vpc_id      = module.vpc_dr.vpc_id

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-alb-sg-dr"
  }
}

# ========================================
# Route53 Health Checks and Failover
# ========================================

resource "aws_route53_health_check" "primary" {
  provider = aws.global

  fqdn              = aws_lb.primary.dns_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name = "${var.project_name}-health-check-primary"
  }
}

resource "aws_route53_zone" "main" {
  provider = aws.global
  count    = var.create_hosted_zone ? 1 : 0

  name = var.domain_name

  tags = {
    Name        = var.domain_name
    Environment = var.environment
  }
}

resource "aws_route53_record" "primary" {
  provider = aws.global
  count    = var.create_hosted_zone ? 1 : 0

  zone_id = aws_route53_zone.main[0].zone_id
  name    = var.domain_name
  type    = "A"

  set_identifier = "primary"
  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = aws_lb.primary.dns_name
    zone_id                = aws_lb.primary.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.primary.id
}

resource "aws_route53_record" "dr" {
  provider = aws.global
  count    = var.create_hosted_zone ? 1 : 0

  zone_id = aws_route53_zone.main[0].zone_id
  name    = var.domain_name
  type    = "A"

  set_identifier = "dr"
  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = aws_lb.dr.dns_name
    zone_id                = aws_lb.dr.zone_id
    evaluate_target_health = true
  }
}

# ========================================
# RDS Multi-Region Setup
# ========================================

resource "aws_db_instance" "primary" {
  provider = aws.primary

  identifier     = "${var.project_name}-db-primary"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 500
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_primary.id]
  db_subnet_group_name   = aws_db_subnet_group.primary.name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  multi_az               = true
  deletion_protection    = var.environment == "production"
  skip_final_snapshot    = var.environment != "production"
  final_snapshot_identifier = "${var.project_name}-db-primary-final-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  performance_insights_enabled = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Name        = "${var.project_name}-db-primary"
    Region      = "primary"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "primary" {
  provider = aws.primary

  name       = "${var.project_name}-db-subnet-primary"
  subnet_ids = module.vpc_primary.private_subnets

  tags = {
    Name = "${var.project_name}-db-subnet-primary"
  }
}

resource "aws_security_group" "rds_primary" {
  provider = aws.primary

  name        = "${var.project_name}-rds-sg-primary"
  description = "Security group for RDS in primary region"
  vpc_id      = module.vpc_primary.vpc_id

  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.primary_vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg-primary"
  }
}

# RDS Read Replica in DR region
resource "aws_db_instance" "dr_replica" {
  provider = aws.dr

  identifier     = "${var.project_name}-db-dr-replica"
  replicate_source_db = aws_db_instance.primary.arn

  instance_class = "db.r6g.large"

  vpc_security_group_ids = [aws_security_group.rds_dr.id]

  backup_retention_period = 7
  skip_final_snapshot     = var.environment != "production"

  performance_insights_enabled = true

  tags = {
    Name        = "${var.project_name}-db-dr-replica"
    Region      = "dr"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds_dr" {
  provider = aws.dr

  name        = "${var.project_name}-rds-sg-dr"
  description = "Security group for RDS in DR region"
  vpc_id      = module.vpc_dr.vpc_id

  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.dr_vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg-dr"
  }
}

# ========================================
# S3 Cross-Region Replication
# ========================================

resource "aws_s3_bucket" "primary" {
  provider = aws.primary
  bucket   = "${var.project_name}-data-primary-${var.environment}"

  tags = {
    Name        = "${var.project_name}-data-primary"
    Region      = "primary"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "primary" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "dr" {
  provider = aws.dr
  bucket   = "${var.project_name}-data-dr-${var.environment}"

  tags = {
    Name        = "${var.project_name}-data-dr"
    Region      = "dr"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "dr" {
  provider = aws.dr
  bucket   = aws_s3_bucket.dr.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_iam_role" "replication" {
  provider = aws.primary
  name     = "${var.project_name}-s3-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "replication" {
  provider = aws.primary
  name     = "${var.project_name}-s3-replication-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.primary.arn
        ]
      },
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.primary.arn}/*"
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.dr.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "replication" {
  provider   = aws.primary
  role       = aws_iam_role.replication.name
  policy_arn = aws_iam_policy.replication.arn
}

resource "aws_s3_bucket_replication_configuration" "primary_to_dr" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary.id
  role     = aws_iam_role.replication.arn

  rule {
    id     = "replicate-all"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.dr.arn
      storage_class = "STANDARD_IA"
    }
  }

  depends_on = [
    aws_s3_bucket_versioning.primary,
    aws_s3_bucket_versioning.dr
  ]
}
