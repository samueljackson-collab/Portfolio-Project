output "vpc_id" {
  description = "ID of the created VPC"
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

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.this.id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway when created"
  value       = try(aws_nat_gateway.this[0].id, "")
}

output "route_table_ids" {
  description = "Route table IDs for public and private subnets"
  value = {
    public  = aws_route_table.public.id
    private = aws_route_table.private.id
  }
}
