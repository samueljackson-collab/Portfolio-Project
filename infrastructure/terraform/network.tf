resource "aws_vpc" "portfolio" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-vpc"
  })
}

resource "aws_subnet" "public" {
  for_each = var.public_subnets

  vpc_id                  = aws_vpc.portfolio.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-public-${each.key}"
    "kubernetes.io/role/elb" = "1"
  })
}

resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.portfolio.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-private-${each.key}"
    "kubernetes.io/role/internal-elb" = "1"
  })
}

resource "aws_internet_gateway" "portfolio" {
  vpc_id = aws_vpc.portfolio.id

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-igw"
  })
}

resource "aws_eip" "nat" {
  count      = length(var.private_subnets)
  vpc        = true
  depends_on = [aws_internet_gateway.portfolio]

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-nat-${count.index}"
  })
}

resource "aws_nat_gateway" "portfolio" {
  for_each = var.public_subnets

  allocation_id = aws_eip.nat[tonumber(each.value.order)].id
  subnet_id     = aws_subnet.public[each.key].id

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-nat-${each.key}"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.portfolio.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.portfolio.id
  }

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  for_each = aws_nat_gateway.portfolio

  vpc_id = aws_vpc.portfolio.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = each.value.id
  }

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-private-rt-${each.key}"
  })
}

resource "aws_route_table_association" "private" {
  for_each       = aws_subnet.private
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[each.value.availability_zone].id
}
