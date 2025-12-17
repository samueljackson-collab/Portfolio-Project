// VPC, subnets (public/private/database), IGW, NAT, tags
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(var.tags, { Name = "${var.project_name}-${var.environment}-vpc" })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = merge(var.tags, { Name = "${var.project_name}-${var.environment}-igw" })
}

resource "aws_subnet" "public" {
  count                    = length(var.azs)
  vpc_id                   = aws_vpc.main.id
  cidr_block               = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone        = var.azs[count.index]
  map_public_ip_on_launch  = true
  tags = merge(var.tags, { Name = "${var.project_name}-${var.environment}-public-${count.index + 1}", Tier = "public" })
}

resource "aws_subnet" "private" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.azs[count.index]
  tags = merge(var.tags, { Name = "${var.project_name}-${var.environment}-private-${count.index + 1}", Tier = "private" })
}
