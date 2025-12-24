terraform {
  required_version = ">= 1.4"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "portfolio-vpc-${var.environment}"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment == "production" ? false : true
  enable_dns_hostnames = true
  enable_dns_support   = true

  create_database_subnet_group = true
  database_subnets             = var.database_subnet_cidrs

  tags = {
    Environment = var.environment
    Project     = "portfolio"
    ManagedBy   = "terraform"
    AutoRecover = "true"
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = "portfolio-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    primary = {
      min_size     = 2
      max_size     = 10
      desired_size = 3

      instance_types = ["t3.medium"]
      capacity_type  = "SPOT"

      health_check_type = "ELB"
      enable_monitoring = true

      mixed_instances_policy = {
        instances_distribution = {
          on_demand_base_capacity                  = 1
          on_demand_percentage_above_base_capacity = 50
          spot_allocation_strategy                 = "capacity-optimized"
        }
        override = [
          {
            instance_type = "t3.medium"
          },
          {
            instance_type = "t3.large"
          },
          {
            instance_type = "t2.medium"
          }
        ]
      }

      tags = {
        "k8s.io/cluster-autoscaler/enabled" = "true"
        "k8s.io/cluster-autoscaler/portfolio" = "owned"
      }
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }
}

resource "aws_security_group" "alb" {
  name        = "portfolio-alb-${var.environment}"
  description = "Allow inbound HTTP traffic to ALB"
  vpc_id      = module.vpc.vpc_id

  ingress {
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
    Name        = "portfolio-alb-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_security_group" "web" {
  name        = "portfolio-web-${var.environment}"
  description = "Allow traffic from ALB to web tier"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "portfolio-web-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_lb" "app" {
  name               = "portfolio-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "production"
  idle_timeout               = 60

  tags = {
    Environment = var.environment
    Project     = "portfolio"
  }
}

resource "aws_lb_target_group" "app" {
  name        = "portfolio-app-${var.environment}"
  port        = 80
  protocol    = "HTTP"
  target_type = "instance"
  vpc_id      = module.vpc.vpc_id

  health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    path                = "/"
    matcher             = "200-399"
  }

  tags = {
    Environment = var.environment
    Project     = "portfolio"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_iam_role" "web_instance" {
  name = "portfolio-web-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  ]
}

resource "aws_iam_instance_profile" "web_instance" {
  name = "portfolio-web-${var.environment}"
  role = aws_iam_role.web_instance.name
}

resource "aws_launch_template" "web" {
  name_prefix   = "portfolio-web-${var.environment}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.web_instance_type

  vpc_security_group_ids = [aws_security_group.web.id]

  iam_instance_profile {
    name = aws_iam_instance_profile.web_instance.name
  }

  user_data = base64encode(<<-EOT
              #!/bin/bash
              dnf install -y nginx
              cat <<'HTML' > /usr/share/nginx/html/index.html
              <html>
                <head><title>Portfolio Web Tier</title></head>
                <body>
                  <h1>Portfolio Web Tier (${var.environment})</h1>
                  <p>Served via Auto Scaling Group behind ALB.</p>
                </body>
              </html>
              HTML
              systemctl enable nginx
              systemctl start nginx
            EOT)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "portfolio-web-${var.environment}"
      Environment = var.environment
      Project     = "portfolio"
    }
  }
}

resource "aws_autoscaling_group" "web" {
  name                      = "portfolio-web-${var.environment}"
  desired_capacity          = var.web_desired_capacity
  max_size                  = var.web_max_size
  min_size                  = var.web_min_size
  vpc_zone_identifier       = module.vpc.private_subnets
  health_check_type         = "ELB"
  health_check_grace_period = 120
  target_group_arns         = [aws_lb_target_group.app.arn]

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "portfolio-web-${var.environment}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "portfolio-${var.environment}"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.t3.medium"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "portfolio"
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [module.vpc.default_security_group_id]

  backup_window      = "03:00-04:00"
  maintenance_window = "Mon:04:00-Mon:05:00"

  backup_retention_period = 7
  skip_final_snapshot     = var.environment != "production"
  deletion_protection     = var.environment == "production"

  performance_insights_enabled = true

  tags = {
    Environment = var.environment
    Project     = "portfolio"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "assets" {
  bucket = var.asset_bucket_name

  tags = {
    Environment = var.environment
    Project     = "portfolio"
  }
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

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_identity" "assets" {
  comment = "OAI for ${aws_s3_bucket.assets.bucket}"
}

resource "aws_s3_bucket_policy" "assets" {
  bucket = aws_s3_bucket.assets.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontRead"
        Effect    = "Allow"
        Principal = { AWS = aws_cloudfront_origin_access_identity.assets.iam_arn }
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.assets.arn}/*"
      }
    ]
  })
}

resource "aws_cloudfront_distribution" "portfolio" {
  enabled         = true
  price_class     = var.cloudfront_price_class
  is_ipv6_enabled = true

  origin {
    domain_name = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id   = "s3-assets"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.assets.cloudfront_access_identity_path
    }
  }

  origin {
    domain_name = aws_lb.app.dns_name
    origin_id   = "alb-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-assets"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  ordered_cache_behavior {
    path_pattern     = "/api/*"
    target_origin_id = "alb-origin"
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Content-Type", "User-Agent"]
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Environment = var.environment
    Project     = "portfolio"
  }
}
