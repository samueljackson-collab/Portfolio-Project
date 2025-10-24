locals {
  vpc_name = "${var.project_name}-${var.environment}-vpc"

  public_subnets   = zipmap(var.availability_zones, var.public_subnet_cidrs)
  private_subnets  = zipmap(var.availability_zones, var.private_app_subnet_cidrs)
  database_subnets = zipmap(var.availability_zones, var.database_subnet_cidrs)
}

resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge({
    Name = local.vpc_name
  }, var.tags)
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge({
    Name = "${var.project_name}-${var.environment}-igw"
  }, var.tags)
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = true

  tags = merge({
    Name = "${var.project_name}-${var.environment}-public-${each.key}",
    Tier = "public"
  }, var.tags)
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value
  availability_zone = each.key

  tags = merge({
    Name = "${var.project_name}-${var.environment}-private-${each.key}",
    Tier = "application"
  }, var.tags)
}

resource "aws_subnet" "database" {
  for_each = local.database_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value
  availability_zone = each.key

  tags = merge({
    Name = "${var.project_name}-${var.environment}-database-${each.key}",
    Tier = "database"
  }, var.tags)
}

resource "aws_eip" "nat" {
  for_each = aws_subnet.public

  domain = "vpc"

  tags = merge({
    Name = "${var.project_name}-${var.environment}-nat-eip-${each.key}"
  }, var.tags)

  depends_on = [aws_internet_gateway.this]
}

resource "aws_nat_gateway" "this" {
  for_each = aws_subnet.public

  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = aws_subnet.public[each.key].id

  tags = merge({
    Name = "${var.project_name}-${var.environment}-nat-${each.key}"
  }, var.tags)
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge({
    Name = "${var.project_name}-${var.environment}-public-rt"
  }, var.tags)
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  for_each = aws_nat_gateway.this

  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = each.value.id
  }

  tags = merge({
    Name = "${var.project_name}-${var.environment}-private-rt-${each.key}"
  }, var.tags)
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[each.key].id
}

resource "aws_route_table" "database" {
  vpc_id = aws_vpc.this.id

  tags = merge({
    Name = "${var.project_name}-${var.environment}-database-rt"
  }, var.tags)
}

resource "aws_route_table_association" "database" {
  for_each = aws_subnet.database

  subnet_id      = each.value.id
  route_table_id = aws_route_table.database.id
}
