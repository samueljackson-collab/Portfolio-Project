output "vpc_id" {
  description = "VPC identifier"
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "nat_gateway_id" {
  description = "NAT Gateway ID when provisioned"
  value       = try(aws_nat_gateway.this[0].id, null)
}

output "flow_log_group_name" {
  description = "CloudWatch Log Group name for flow logs"
  value       = try(aws_cloudwatch_log_group.flow_logs[0].name, null)
}
