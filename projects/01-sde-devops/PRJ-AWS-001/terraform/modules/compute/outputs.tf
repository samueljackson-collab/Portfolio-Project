output "alb_dns_name" {
  value       = aws_lb.app.dns_name
  description = "Public DNS name for the application load balancer"
}

output "alb_arn" {
  value       = aws_lb.app.arn
  description = "ARN for the ALB"
}

output "alb_arn_suffix" {
  value       = aws_lb.app.arn_suffix
  description = "ALB metric dimension name"
}

output "alb_security_group_id" {
  value       = var.alb_security_group_id
  description = "Pass-through of ALB security group ID"
}

output "asg_name" {
  value       = aws_autoscaling_group.app.name
  description = "Auto Scaling Group name"
}

output "launch_template_id" {
  value       = aws_launch_template.app.id
  description = "Launch template ID"
}
