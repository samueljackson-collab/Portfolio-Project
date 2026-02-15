output "launch_template_id" {
  description = "ID of the launch template powering the Auto Scaling group."
  value       = aws_launch_template.this.id
}

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling group."
  value       = aws_autoscaling_group.this.name
}

output "instance_profile_name" {
  description = "IAM instance profile attached to application instances."
  value       = aws_iam_instance_profile.this.name
}
