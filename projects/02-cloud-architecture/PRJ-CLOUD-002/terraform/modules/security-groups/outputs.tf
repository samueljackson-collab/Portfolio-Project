output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer."
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "Security group ID for the application Auto Scaling group."
  value       = aws_security_group.app.id
}

output "database_security_group_id" {
  description = "Security group ID for the PostgreSQL database."
  value       = aws_security_group.database.id
}
