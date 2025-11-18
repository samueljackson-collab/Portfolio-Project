terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  az_count    = min(var.az_count, length(data.aws_availability_zones.available.names))

  base_tags = merge(
    var.tags,
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = var.enable_dns_support
  enable_dns_hostnames = var.enable_dns_hostnames

  tags = merge(
    local.base_tags,
    { Name = "${local.name_prefix}-vpc" }
  )
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-igw" })
}

resource "aws_subnet" "public" {
  count                   = local.az_count
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = merge(
    local.base_tags,
    {
      Name = "${local.name_prefix}-public-subnet-${count.index + 1}"
      Tier = "public"
    }
  )
}

resource "aws_subnet" "private" {
  count             = local.az_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + local.az_count)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(
    local.base_tags,
    {
      Name = "${local.name_prefix}-private-subnet-${count.index + 1}"
      Tier = "private"
    }
  )
}

resource "aws_subnet" "database" {
  count             = local.az_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + (local.az_count * 2))
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(
    local.base_tags,
    {
      Name = "${local.name_prefix}-database-subnet-${count.index + 1}"
      Tier = "database"
    }
  )
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : local.az_count) : 0
  domain = "vpc"

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-nat-eip-${count.index + 1}" })

  depends_on = [aws_internet_gateway.this]
}

resource "aws_nat_gateway" "this" {
  count         = length(aws_eip.nat)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[var.single_nat_gateway ? 0 : count.index].id

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-nat-${count.index + 1}" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-public-rt" })
}

resource "aws_route_table_association" "public" {
  count          = local.az_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  count = length(aws_nat_gateway.this)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this[var.single_nat_gateway ? 0 : count.index].id
  }

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-private-rt-${count.index + 1}" })
}

resource "aws_route_table_association" "private" {
  count          = local.az_count
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[var.single_nat_gateway ? 0 : count.index].id
}

resource "aws_vpc_endpoint" "s3" {
  count             = var.enable_s3_endpoint ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat([aws_route_table.public.id], aws_route_table.private[*].id)

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-s3-endpoint" })
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count             = var.enable_flow_logs ? 1 : 0
  name              = "/aws/vpc/${local.name_prefix}/flow-logs"
  retention_in_days = var.flow_logs_retention_days

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-flow-logs" })
}

resource "aws_flow_log" "this" {
  count          = var.enable_flow_logs ? 1 : 0
  log_destination = aws_cloudwatch_log_group.flow_logs[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the vpc"
}

output "public_subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "Public subnet identifiers"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "Private subnet identifiers"
}

output "database_subnet_ids" {
  value       = aws_subnet.database[*].id
  description = "Database subnet identifiers"
}

variable "project_name" {
  description = "Name of the project using the vpc"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_cidr" {
  description = "Primary cidr block for the VPC"
  type        = string
}

variable "az_count" {
  description = "Number of availability zones to span"
  type        = number
  default     = 2
}

variable "enable_nat_gateway" {
  description = "Toggle NAT gateway provisioning"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use one NAT gateway to minimize spend"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS resolution inside the VPC"
  type        = bool
  default     = true
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames inside the VPC"
  type        = bool
  default     = true
}

variable "map_public_ip_on_launch" {
  description = "Assign public IPs to instances in public subnet"
  type        = bool
  default     = true
}

variable "enable_s3_endpoint" {
  description = "Create an S3 gateway endpoint"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs for auditing"
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "Retention for flow log data"
  type        = number
  default     = 14
}

variable "aws_region" {
  description = "AWS region used to build the S3 endpoint name"
  type        = string
}

variable "tags" {
  description = "Additional tags for the VPC and subnets"
  type        = map(string)
  default     = {}
}
