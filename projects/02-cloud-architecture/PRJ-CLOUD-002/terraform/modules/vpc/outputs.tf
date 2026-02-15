output "vpc_id" {
  description = "Identifier of the VPC."
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets that host internet-facing resources."
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_app_subnet_ids" {
  description = "IDs of the private application subnets."
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "private_db_subnet_ids" {
  description = "IDs of the isolated database subnets."
  value       = [for subnet in aws_subnet.database : subnet.id]
}

output "database_subnet_ids" {
  description = "Alias for private_db_subnet_ids for compatibility."
  value       = [for subnet in aws_subnet.database : subnet.id]
}

output "nat_gateway_ids" {
  description = "IDs of the NAT gateways providing egress for private subnets."
  value       = [for nat in values(aws_nat_gateway.this) : nat.id]
}
