# terraform/outputs.tf
#
# Outputs are values displayed after Terraform creates infrastructure.
# They provide critical information needed to access and manage resources.

# ========================================
# Load Balancer Outputs
# ========================================

output "load_balancer_dns" {
  description = "DNS name of the load balancer (use this to access your application)"
  value       = aws_lb.main.dns_name
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer (for Route53 alias records)"
  value       = aws_lb.main.zone_id
}

output "alb_target_group_arn" {
  description = "ARN of the load balancer target group"
  value       = aws_lb_target_group.app.arn
}

# ========================================
# Database Outputs
# ========================================

output "database_endpoint" {
  description = "RDS database endpoint (hostname:port)"
  value       = aws_db_instance.main.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
  sensitive   = false
}

output "database_password_secret_arn" {
  description = "ARN of Secrets Manager secret containing database password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "database_connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = "postgresql://${aws_db_instance.main.username}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
}

# ========================================
# VPC Outputs
# ========================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "database_subnet_ids" {
  description = "IDs of database subnets"
  value       = [for subnet in aws_subnet.database : subnet.id]
}

# ========================================
# Auto Scaling Outputs
# ========================================

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}

output "autoscaling_group_arn" {
  description = "ARN of the Auto Scaling Group"
  value       = aws_autoscaling_group.app.arn
}

output "launch_template_id" {
  description = "ID of the Launch Template"
  value       = aws_launch_template.app.id
}

# ========================================
# Security Group Outputs
# ========================================

output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "ID of the application security group"
  value       = aws_security_group.app.id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

# ========================================
# Monitoring Outputs
# ========================================

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch Log Group for application logs"
  value       = var.enable_cloudwatch_logs ? aws_cloudwatch_log_group.app[0].name : "CloudWatch logs not enabled"
}

output "vpc_flow_log_group_name" {
  description = "Name of the CloudWatch Log Group for VPC flow logs"
  value       = aws_cloudwatch_log_group.vpc_flow_logs.name
}

# ========================================
# Helpful Commands
# ========================================

output "connection_commands" {
  description = "Helpful commands to connect to resources"
  value = <<-EOT
    
    🎉 Infrastructure Created Successfully!
    
    ========================================
    Access Your Application:
    ========================================
    
    Load Balancer URL: http://${aws_lb.main.dns_name}
    
    (It may take 2-3 minutes for instances to become healthy)
    
    ========================================
    Database Connection:
    ========================================
    
    # Retrieve database password:
    aws secretsmanager get-secret-value \
      --secret-id ${aws_secretsmanager_secret.db_password.arn} \
      --query SecretString \
      --output text | jq -r '.password'
    
    # Connect to database (from instance in private subnet):
    psql -h ${aws_db_instance.main.address} \
         -U ${aws_db_instance.main.username} \
         -d ${aws_db_instance.main.db_name}
    
    ========================================
    Monitoring:
    ========================================
    
    # View Auto Scaling Group status:
    aws autoscaling describe-auto-scaling-groups \
      --auto-scaling-group-names ${aws_autoscaling_group.app.name}
    
    # View load balancer target health:
    aws elbv2 describe-target-health \
      --target-group-arn ${aws_lb_target_group.app.arn}
    
    # View CloudWatch logs:
    aws logs tail ${aws_cloudwatch_log_group.vpc_flow_logs.name} --follow
    
    ========================================
    Cost Tracking:
    ========================================
    
    Estimated monthly cost: $${ceil((2 * 7.50) + 30 + (2 * 45) + 5)} 
    - EC2 instances (2x t3.micro): ~$15
    - RDS db.t3.micro (Multi-AZ): ~$30
    - NAT Gateways (2x): ~$90
    - ALB: ~$20
    - Data transfer & misc: ~$5
    
    To reduce costs:
    - Set db_multi_az = false (-$15/month)
    - Use 1 NAT Gateway instead of 2 (-$45/month)
    - Stop RDS during non-business hours (up to -70%)
    
  EOT
}

