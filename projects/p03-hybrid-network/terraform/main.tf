# Hybrid Network Connectivity - VPN Connection
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Simulated On-Premises VPC (VPC1)
resource "aws_vpc" "onprem" {
  cidr_block           = "192.168.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "OnPrem-VPC"
  }
}

# AWS Cloud VPC (VPC2)
resource "aws_vpc" "cloud" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "Cloud-VPC"
  }
}

# Customer Gateway (represents on-prem VPN endpoint)
resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = var.customer_gateway_ip
  type       = "ipsec.1"

  tags = {
    Name = "OnPrem-Customer-Gateway"
  }
}

# Virtual Private Gateway
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.cloud.id

  tags = {
    Name = "Cloud-VPN-Gateway"
  }
}

# Site-to-Site VPN Connection
resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.main.id
  type                = "ipsec.1"
  static_routes_only  = true

  tags = {
    Name = "Hybrid-VPN-Connection"
  }
}

# VPN Static Routes
resource "aws_vpn_connection_route" "onprem" {
  destination_cidr_block = aws_vpc.onprem.cidr_block
  vpn_connection_id      = aws_vpn_connection.main.id
}

# Route Table for Cloud VPC
resource "aws_route_table" "cloud_private" {
  vpc_id = aws_vpc.cloud.id

  route {
    cidr_block = aws_vpc.onprem.cidr_block
    gateway_id = aws_vpn_gateway.main.id
  }

  tags = {
    Name = "Cloud-Private-RT"
  }
}

# Security Group for Hybrid Connectivity
resource "aws_security_group" "hybrid" {
  name        = "hybrid-connectivity"
  description = "Allow traffic from on-prem network"
  vpc_id      = aws_vpc.cloud.id

  ingress {
    description = "Allow from on-prem"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.onprem.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Hybrid-Security-Group"
  }
}

variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "customer_gateway_ip" {
  description = "Public IP of on-premises VPN endpoint"
  type        = string
}

output "vpn_connection_id" {
  value = aws_vpn_connection.main.id
}

output "cloud_vpc_id" {
  value = aws_vpc.cloud.id
}

output "onprem_vpc_id" {
  value = aws_vpc.onprem.id
}
