resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_subnet" "public" {
  for_each          = toset(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.this.id
  cidr_block        = each.key
  map_public_ip_on_launch = true
}

resource "aws_subnet" "private" {
  for_each   = toset(var.private_subnet_cidrs)
  vpc_id     = aws_vpc.this.id
  cidr_block = each.key
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  value = [for subnet in aws_subnet.private : subnet.id]
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = set(string)
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs"
  type        = set(string)
}
