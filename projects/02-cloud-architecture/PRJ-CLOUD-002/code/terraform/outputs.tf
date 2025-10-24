output "vpc_id" {
  description = "Identifier of the provisioned VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets hosting ingress resources"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets for the application tier"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of subnets dedicated to the database tier"
  value       = aws_subnet.database[*].id
}

output "alb_dns_name" {
  description = "Public DNS name for the Application Load Balancer"
  value       = aws_lb.app.dns_name
}

output "alb_zone_id" {
  description = "Hosted zone ID for ALB – useful when creating Route 53 records"
  value       = aws_lb.app.zone_id
}

output "rds_endpoint" {
  description = "Writer endpoint for the PostgreSQL instance"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}

