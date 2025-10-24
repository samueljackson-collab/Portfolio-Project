resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-vpc"
  })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-igw"
  })
}

resource "aws_subnet" "public" {
  for_each = { for index, cidr in var.public_subnets : index => cidr }

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-public-${each.key}"
    Tier = "public"
  })
}

resource "aws_subnet" "private" {
  for_each = { for index, cidr in var.private_subnets : index => cidr }

  vpc_id     = aws_vpc.this.id
  cidr_block = each.value

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-private-${each.key}"
    Tier = "app"
  })
}

resource "aws_subnet" "data" {
  for_each = { for index, cidr in var.data_subnets : index => cidr }

  vpc_id     = aws_vpc.this.id
  cidr_block = each.value

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-data-${each.key}"
    Tier = "data"
  })
}

resource "aws_security_group" "app" {
  name        = "${var.project}-${var.environment}-app"
  description = "App security group"
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "Allow HTTP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-app-sg"
  })
}

resource "aws_security_group" "db" {
  name        = "${var.project}-${var.environment}-db"
  description = "DB security group"
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "Postgres"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-db-sg"
  })
}
