terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.37.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_vpc" "pen_test" {
  cidr_block = "10.50.0.0/16"
  tags = { Name = "external-pen-test" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.pen_test.id
  cidr_block              = "10.50.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.region}a"
  tags = { Name = "external-pen-test-public" }
}

resource "aws_security_group" "ecs" {
  name        = "pen-test-ecs"
  description = "Allow HTTP"
  vpc_id      = aws_vpc.pen_test.id

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
}

resource "aws_iam_role" "ecs_task" {
  name = "pen-test-ecs-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_db_subnet_group" "pen_test" {
  name       = "pen-test-subnets"
  subnet_ids = [aws_subnet.public.id]
}

resource "aws_db_instance" "pen_test" {
  identifier              = "pen-test-db"
  allocated_storage       = 20
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = "db.t3.micro"
  username                = var.db_username
  password                = var.db_password
  publicly_accessible     = true
  vpc_security_group_ids  = [aws_security_group.ecs.id]
  skip_final_snapshot     = true
  db_subnet_group_name    = aws_db_subnet_group.pen_test.name
}

resource "aws_ecr_repository" "backend" {
  name = "external-pen-test-backend"
}

resource "aws_ecs_cluster" "pen_test" {
  name = "external-pen-test"
}

resource "aws_lb" "frontend" {
  name               = "pen-test-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public.id]
  security_groups    = [aws_security_group.ecs.id]
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.prefix}-pen-test-frontend"
}

resource "aws_cloudfront_distribution" "cdn" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "s3-origin"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-origin"
    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

resource "aws_launch_template" "ecs" {
  name_prefix   = "pen-test-ecs"
  image_id      = data.aws_ami.ecs.id
  instance_type = "t3.small"
}

data "aws_ami" "ecs" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
}

resource "aws_autoscaling_group" "ecs" {
  name                      = "pen-test-ecs-asg"
  max_size                  = 2
  min_size                  = 1
  desired_capacity          = 1
  vpc_zone_identifier       = [aws_subnet.public.id]
  launch_template {
    id      = aws_launch_template.ecs.id
    version = "$Latest"
  }
}
