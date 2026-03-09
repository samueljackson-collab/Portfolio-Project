# Networking Module Outputs
# Purpose: Export VPC and subnet IDs for use by other modules

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs (one per AZ)"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "List of private application subnet IDs (one per AZ)"
  value       = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  description = "List of private database subnet IDs (one per AZ)"
  value       = aws_subnet.private_db[*].id
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_app_route_table_ids" {
  description = "List of private app route table IDs (one per AZ)"
  value       = aws_route_table.private_app[*].id
}

output "private_db_route_table_ids" {
  description = "List of private database route table IDs (one per AZ)"
  value       = aws_route_table.private_db[*].id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = "List of NAT Gateway public IP addresses"
  value       = aws_eip.nat[*].public_ip
}

output "s3_vpc_endpoint_id" {
  description = "ID of S3 VPC Endpoint (if enabled)"
  value       = var.enable_s3_endpoint && length(aws_vpc_endpoint.s3) > 0 ? aws_vpc_endpoint.s3[0].id : null
}

output "dynamodb_vpc_endpoint_id" {
  description = "ID of DynamoDB VPC Endpoint (if enabled)"
  value       = var.enable_dynamodb_endpoint && length(aws_vpc_endpoint.dynamodb) > 0 ? aws_vpc_endpoint.dynamodb[0].id : null
}

output "vpc_flow_log_group_name" {
  description = "Name of CloudWatch Log Group for VPC Flow Logs"
  value       = var.enable_vpc_flow_logs && length(aws_cloudwatch_log_group.flow_logs) > 0 ? aws_cloudwatch_log_group.flow_logs[0].name : null
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = var.availability_zones
}

output "public_subnet_cidr_blocks" {
  description = "CIDR blocks of public subnets"
  value       = aws_subnet.public[*].cidr_block
}

output "private_app_subnet_cidr_blocks" {
  description = "CIDR blocks of private app subnets"
  value       = aws_subnet.private_app[*].cidr_block
}

output "private_db_subnet_cidr_blocks" {
  description = "CIDR blocks of private database subnets"
  value       = aws_subnet.private_db[*].cidr_block
}

output "subnet_groups" {
  description = "Map of subnet groups for easier reference"
  value = {
    public      = aws_subnet.public[*].id
    private_app = aws_subnet.private_app[*].id
    private_db  = aws_subnet.private_db[*].id
  }
}

output "routing_summary" {
  description = "Summary of routing configuration for documentation"
  value = {
    public_subnets = {
      route_table      = aws_route_table.public.id
      internet_gateway = aws_internet_gateway.main.id
      nat_gateway      = "N/A"
    }
    private_app_subnets = {
      route_tables      = aws_route_table.private_app[*].id
      internet_gateway  = "N/A"
      nat_gateways      = aws_nat_gateway.main[*].id
    }
    private_db_subnets = {
      route_tables    = aws_route_table.private_db[*].id
      internet_access = "None"
    }
  }
}
