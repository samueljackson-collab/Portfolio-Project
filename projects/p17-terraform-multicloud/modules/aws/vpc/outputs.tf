output "vpc_id" {
  description = "VPC ID."
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = values(aws_subnet.public)[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs."
  value       = values(aws_subnet.private)[*].id
}

output "nat_gateway_ids" {
  description = "NAT gateway IDs."
  value       = var.enable_nat_gateway ? values(aws_nat_gateway.this)[*].id : []
}

output "vpc_endpoint_ids" {
  description = "VPC endpoint IDs."
  value       = concat(values(aws_vpc_endpoint.gateway)[*].id, values(aws_vpc_endpoint.interface)[*].id)
}

output "flow_log_id" {
  description = "Flow log ID when enabled."
  value       = var.enable_flow_logs ? aws_flow_log.this[0].id : null
}
