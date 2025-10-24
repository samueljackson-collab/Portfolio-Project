output "alb_arn" {
  description = "ARN of the Application Load Balancer."
  value       = aws_lb.this.arn
}

output "alb_name" {
  description = "Name of the Application Load Balancer."
  value       = aws_lb.this.name
}

output "alb_dns_name" {
  description = "DNS name to reach the ALB."
  value       = aws_lb.this.dns_name
}

output "alb_arn_suffix" {
  description = "ARN suffix used for CloudWatch metrics."
  value       = aws_lb.this.arn_suffix
}

output "target_group_arn" {
  description = "ARN of the target group registered with the Auto Scaling group."
  value       = aws_lb_target_group.this.arn
}

output "target_group_arn_suffix" {
  description = "ARN suffix of the target group for CloudWatch metrics."
  value       = aws_lb_target_group.this.arn_suffix
}
