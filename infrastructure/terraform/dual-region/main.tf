terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}

provider "aws" {
  region = var.primary_region
}

provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
}

locals {
  regions = {
    primary = {
      provider = aws
      cidr     = cidrsubnet(var.vpc_cidr_base, 4, 0)
      name     = "${var.project}-primary"
    }
    secondary = {
      provider = aws.secondary
      cidr     = cidrsubnet(var.vpc_cidr_base, 4, 1)
      name     = "${var.project}-secondary"
    }
  }
  common_tags = {
    Project = var.project
    Owner   = var.owner
    Purpose = "roaming-simulation"
  }
}

resource "random_id" "suffix" {
  byte_length = 2
}

resource "aws_vpc" "regional" {
  for_each             = local.regions
  provider             = each.value.provider
  cidr_block           = each.value.cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = merge(local.common_tags, {
    Name   = "${each.value.name}-vpc"
    Region = each.key
  })
}

resource "aws_subnet" "public" {
  for_each = local.regions
  provider = each.value.provider
  vpc_id   = aws_vpc.regional[each.key].id
  cidr_block = cidrsubnet(each.value.cidr, 4, 0)
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.all[each.key].names[0]
  tags = merge(local.common_tags, {
    Name   = "${each.value.name}-public"
    Region = each.key
  })
}

resource "aws_subnet" "private" {
  for_each = local.regions
  provider = each.value.provider
  vpc_id   = aws_vpc.regional[each.key].id
  cidr_block = cidrsubnet(each.value.cidr, 4, 1)
  map_public_ip_on_launch = false
  availability_zone       = data.aws_availability_zones.all[each.key].names[1]
  tags = merge(local.common_tags, {
    Name   = "${each.value.name}-private"
    Region = each.key
  })
}

data "aws_availability_zones" "all" {
  for_each = local.regions
  provider = each.value.provider
  state    = "available"
}

resource "aws_internet_gateway" "regional" {
  for_each = local.regions
  provider = each.value.provider
  vpc_id   = aws_vpc.regional[each.key].id
  tags = merge(local.common_tags, { Name = "${each.value.name}-igw" })
}

resource "aws_route_table" "public" {
  for_each = local.regions
  provider = each.value.provider
  vpc_id   = aws_vpc.regional[each.key].id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.regional[each.key].id
  }
  tags = merge(local.common_tags, { Name = "${local.regions[each.key].name}-public-rt" })
}

resource "aws_route_table_association" "public_association" {
  for_each       = local.regions
  provider       = each.value.provider
  subnet_id      = aws_subnet.public[each.key].id
  route_table_id = aws_route_table.public[each.key].id
}

resource "aws_security_group" "api" {
  for_each    = local.regions
  provider    = each.value.provider
  name        = "${local.regions[each.key].name}-api"
  description = "Allow HTTPS and OTLP"
  vpc_id      = aws_vpc.regional[each.key].id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 4317
    to_port     = 4318
    protocol    = "tcp"
    cidr_blocks = [var.peer_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, { Name = "${local.regions[each.key].name}-api" })
}

resource "aws_lb" "api" {
  for_each = local.regions
  provider = each.value.provider
  name               = "${local.regions[each.key].name}-alb"
  load_balancer_type = "application"
  subnets            = [aws_subnet.public[each.key].id]
  security_groups    = [aws_security_group.api[each.key].id]
  tags               = merge(local.common_tags, { Name = "${local.regions[each.key].name}-alb" })
}

output "regional_vpcs" {
  value = { for k, v in aws_vpc.regional : k => {
    id     = v.id
    cidr   = v.cidr_block
    region = k
  } }
}

output "api_endpoints" {
  value = { for k, lb in aws_lb.api : k => lb.dns_name }
  description = "Regional ALB endpoints for the roaming FastAPI service"
}
