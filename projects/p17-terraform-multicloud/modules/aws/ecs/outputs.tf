output "cluster_id" {
  description = "ECS cluster ID."
  value       = aws_ecs_cluster.this.id
}

output "service_name" {
  description = "ECS service name."
  value       = aws_ecs_service.this.name
}

output "task_definition_arn" {
  description = "Task definition ARN."
  value       = aws_ecs_task_definition.this.arn
}

output "security_group_id" {
  description = "Security group ID used by the service."
  value       = length(var.security_group_ids) > 0 ? var.security_group_ids[0] : aws_security_group.service[0].id
}
