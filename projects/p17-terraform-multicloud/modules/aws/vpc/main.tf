data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs             = length(var.azs) > 0 ? var.azs : data.aws_availability_zones.available.names
  public_subnets  = { for idx, cidr in var.public_subnet_cidrs : idx => cidr }
  private_subnets = { for idx, cidr in var.private_subnet_cidrs : idx => cidr }
  nat_subnets     = var.enable_nat_gateway ? aws_subnet.public : {}
  tags            = merge(var.tags, { Project = var.project_name, Environment = var.environment })
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.tags, { Name = "${var.project_name}-vpc" })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = merge(local.tags, { Name = "${var.project_name}-igw" })
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = local.azs[each.key]
  map_public_ip_on_launch = true

  tags = merge(local.tags, {
    Name = "${var.project_name}-public-${each.key}"
    Tier = "public"
  })
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = local.azs[each.key]
  map_public_ip_on_launch = false

  tags = merge(local.tags, {
    Name = "${var.project_name}-private-${each.key}"
    Tier = "private"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(local.tags, { Name = "${var.project_name}-public-rt" })
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  for_each = local.nat_subnets

  domain = "vpc"
  tags   = merge(local.tags, { Name = "${var.project_name}-nat-eip-${each.key}" })
}

resource "aws_nat_gateway" "this" {
  for_each = local.nat_subnets

  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = each.value.id

  tags = merge(local.tags, { Name = "${var.project_name}-nat-${each.key}" })
}

resource "aws_route_table" "private" {
  for_each = aws_subnet.private

  vpc_id = aws_vpc.this.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.this[each.key].id
    }
  }

  tags = merge(local.tags, { Name = "${var.project_name}-private-rt-${each.key}" })
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[each.key].id
}

resource "aws_security_group" "endpoints" {
  count = var.enable_vpc_endpoints && length(var.interface_endpoints) > 0 ? 1 : 0

  name        = "${var.project_name}-vpc-endpoints"
  description = "Security group for VPC interface endpoints"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${var.project_name}-vpc-endpoints" })
}

resource "aws_vpc_endpoint" "gateway" {
  for_each = var.enable_vpc_endpoints ? toset(var.gateway_endpoints) : []

  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.region}.${each.key}"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = values(aws_route_table.private)[*].id

  tags = merge(local.tags, { Name = "${var.project_name}-${each.key}-endpoint" })
}

resource "aws_vpc_endpoint" "interface" {
  for_each = var.enable_vpc_endpoints ? toset(var.interface_endpoints) : []

  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = values(aws_subnet.private)[*].id
  security_group_ids  = [aws_security_group.endpoints[0].id]
  private_dns_enabled = true

  tags = merge(local.tags, { Name = "${var.project_name}-${each.key}-endpoint" })
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name              = "/aws/vpc/${var.project_name}-flow-logs"
  retention_in_days = var.flow_logs_retention_in_days
  tags              = local.tags
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name = "${var.project_name}-vpc-flow-logs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name = "${var.project_name}-vpc-flow-logs"
  role = aws_iam_role.flow_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_flow_log" "this" {
  count = var.enable_flow_logs ? 1 : 0

  iam_role_arn    = aws_iam_role.flow_logs[0].arn
  log_destination = aws_cloudwatch_log_group.flow_logs[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.this.id

  tags = merge(local.tags, { Name = "${var.project_name}-flow-logs" })
}
