locals {
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "ALB security group"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.alb_ingress_cidrs
    content {
      description = "Allow HTTP"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  dynamic "ingress" {
    for_each = var.alb_ingress_cidrs
    content {
      description = "Allow HTTPS"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-alb-sg" })
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Application tier security group"
  vpc_id      = var.vpc_id

  ingress {
    description      = "Allow ALB to reach app instances"
    from_port        = var.app_port
    to_port          = var.app_port
    protocol         = "tcp"
    security_groups  = [aws_security_group.alb.id]
  }

  ingress {
    description = "Allow internal egress"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.bastion_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-app-sg" })
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Database tier security group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow app tier"
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-db-sg" })
}
