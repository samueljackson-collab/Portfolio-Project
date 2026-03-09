###############################################################################
# Networking Module - Outputs
###############################################################################

#------------------------------------------------------------------------------
# VPC Outputs
#------------------------------------------------------------------------------

output "vpc_id" {
  description = "The ID of the VPC."
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC."
  value       = aws_vpc.main.cidr_block
}

output "vpc_arn" {
  description = "The ARN of the VPC."
  value       = aws_vpc.main.arn
}

#------------------------------------------------------------------------------
# Subnet Outputs
#------------------------------------------------------------------------------

output "public_subnet_ids" {
  description = "List of public subnet IDs."
  value       = aws_subnet.public[*].id
}

output "public_subnet_cidrs" {
  description = "List of public subnet CIDR blocks."
  value       = aws_subnet.public[*].cidr_block
}

output "private_subnet_ids" {
  description = "List of private subnet IDs."
  value       = aws_subnet.private[*].id
}

output "private_subnet_cidrs" {
  description = "List of private subnet CIDR blocks."
  value       = aws_subnet.private[*].cidr_block
}

output "database_subnet_ids" {
  description = "List of database subnet IDs."
  value       = aws_subnet.database[*].id
}

output "database_subnet_cidrs" {
  description = "List of database subnet CIDR blocks."
  value       = aws_subnet.database[*].cidr_block
}

output "database_subnet_group_name" {
  description = "Name of the database subnet group."
  value       = aws_db_subnet_group.database.name
}

output "database_subnet_group_id" {
  description = "ID of the database subnet group."
  value       = aws_db_subnet_group.database.id
}

#------------------------------------------------------------------------------
# Gateway Outputs
#------------------------------------------------------------------------------

output "internet_gateway_id" {
  description = "The ID of the Internet Gateway."
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs."
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = "List of NAT Gateway public IP addresses."
  value       = aws_eip.nat[*].public_ip
}

#------------------------------------------------------------------------------
# Route Table Outputs
#------------------------------------------------------------------------------

output "public_route_table_id" {
  description = "The ID of the public route table."
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "List of private route table IDs."
  value       = aws_route_table.private[*].id
}

output "database_route_table_id" {
  description = "The ID of the database route table."
  value       = aws_route_table.database.id
}

#------------------------------------------------------------------------------
# VPC Endpoint Outputs
#------------------------------------------------------------------------------

output "s3_endpoint_id" {
  description = "The ID of the S3 VPC endpoint."
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.s3[0].id : null
}

output "dynamodb_endpoint_id" {
  description = "The ID of the DynamoDB VPC endpoint."
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.dynamodb[0].id : null
}

#------------------------------------------------------------------------------
# Flow Logs Outputs
#------------------------------------------------------------------------------

output "flow_log_id" {
  description = "The ID of the VPC Flow Log."
  value       = var.enable_flow_logs ? aws_flow_log.main[0].id : null
}

output "flow_log_group_name" {
  description = "The name of the CloudWatch Log Group for VPC Flow Logs."
  value       = var.enable_flow_logs ? aws_cloudwatch_log_group.flow_logs[0].name : null
}

#------------------------------------------------------------------------------
# Availability Zone Outputs
#------------------------------------------------------------------------------

output "availability_zones" {
  description = "List of availability zones used."
  value       = var.availability_zones
}
