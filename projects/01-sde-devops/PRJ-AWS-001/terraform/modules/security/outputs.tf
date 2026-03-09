output "alb_security_group_id" {
  description = "Security group ID for Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "Security group ID for application instances"
  value       = aws_security_group.app.id
}

output "db_security_group_id" {
  description = "Security group ID for database instances"
  value       = aws_security_group.db.id
}
