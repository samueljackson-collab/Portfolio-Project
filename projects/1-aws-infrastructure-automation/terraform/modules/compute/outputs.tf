###############################################################################
# Compute Module - Outputs
###############################################################################

#------------------------------------------------------------------------------
# Load Balancer Outputs
#------------------------------------------------------------------------------

output "alb_id" {
  description = "The ID of the Application Load Balancer."
  value       = aws_lb.app.id
}

output "alb_arn" {
  description = "The ARN of the Application Load Balancer."
  value       = aws_lb.app.arn
}

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer."
  value       = aws_lb.app.dns_name
}

output "alb_zone_id" {
  description = "The zone ID of the Application Load Balancer."
  value       = aws_lb.app.zone_id
}

output "alb_arn_suffix" {
  description = "The ARN suffix of the ALB for CloudWatch metrics."
  value       = aws_lb.app.arn_suffix
}

#------------------------------------------------------------------------------
# Target Group Outputs
#------------------------------------------------------------------------------

output "target_group_arn" {
  description = "The ARN of the ALB target group."
  value       = aws_lb_target_group.app.arn
}

output "target_group_name" {
  description = "The name of the ALB target group."
  value       = aws_lb_target_group.app.name
}

output "target_group_arn_suffix" {
  description = "The ARN suffix of the target group for CloudWatch metrics."
  value       = aws_lb_target_group.app.arn_suffix
}

#------------------------------------------------------------------------------
# Auto Scaling Group Outputs
#------------------------------------------------------------------------------

output "asg_id" {
  description = "The ID of the Auto Scaling Group."
  value       = aws_autoscaling_group.app.id
}

output "asg_name" {
  description = "The name of the Auto Scaling Group."
  value       = aws_autoscaling_group.app.name
}

output "asg_arn" {
  description = "The ARN of the Auto Scaling Group."
  value       = aws_autoscaling_group.app.arn
}

#------------------------------------------------------------------------------
# Launch Template Outputs
#------------------------------------------------------------------------------

output "launch_template_id" {
  description = "The ID of the launch template."
  value       = aws_launch_template.app.id
}

output "launch_template_arn" {
  description = "The ARN of the launch template."
  value       = aws_launch_template.app.arn
}

output "launch_template_latest_version" {
  description = "The latest version of the launch template."
  value       = aws_launch_template.app.latest_version
}

#------------------------------------------------------------------------------
# Security Group Outputs
#------------------------------------------------------------------------------

output "alb_security_group_id" {
  description = "The ID of the ALB security group."
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "The ID of the application security group."
  value       = aws_security_group.app.id
}

#------------------------------------------------------------------------------
# IAM Outputs
#------------------------------------------------------------------------------

output "instance_role_arn" {
  description = "The ARN of the EC2 instance IAM role."
  value       = aws_iam_role.instance.arn
}

output "instance_role_name" {
  description = "The name of the EC2 instance IAM role."
  value       = aws_iam_role.instance.name
}

output "instance_profile_arn" {
  description = "The ARN of the instance profile."
  value       = aws_iam_instance_profile.instance.arn
}

output "instance_profile_name" {
  description = "The name of the instance profile."
  value       = aws_iam_instance_profile.instance.name
}
