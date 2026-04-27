# ECS Application Module Outputs

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_service_id" {
  description = "ID of the ECS service"
  value       = aws_ecs_service.app.id
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = aws_ecs_task_definition.app.arn
}

output "task_definition_family" {
  description = "Family of the task definition"
  value       = aws_ecs_task_definition.app.family
}

output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app.arn
}

output "alb_security_group_id" {
  description = "Security group ID of the ALB"
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "Security group ID of the ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

# Structured outputs for downstream modules and documentation
output "target_groups" {
  description = "Structured metadata about the ALB target groups"
  value = {
    application = {
      arn         = aws_lb_target_group.app.arn
      name        = aws_lb_target_group.app.name
      port        = aws_lb_target_group.app.port
      protocol    = aws_lb_target_group.app.protocol
      target_type = aws_lb_target_group.app.target_type
      health_check = {
        path                = aws_lb_target_group.app.health_check[0].path
        matcher             = aws_lb_target_group.app.health_check[0].matcher
        interval            = aws_lb_target_group.app.health_check[0].interval
        timeout             = aws_lb_target_group.app.health_check[0].timeout
        healthy_threshold   = aws_lb_target_group.app.health_check[0].healthy_threshold
        unhealthy_threshold = aws_lb_target_group.app.health_check[0].unhealthy_threshold
      }
    }
  }
}

output "security_groups" {
  description = "Structured metadata about security groups used by the service"
  value = {
    alb = {
      id          = aws_security_group.alb.id
      name        = aws_security_group.alb.name
      description = aws_security_group.alb.description
      ingress_rules = [for rule in aws_security_group.alb.ingress : {
        from_port   = rule.from_port
        to_port     = rule.to_port
        protocol    = rule.protocol
        cidr_blocks = try(rule.cidr_blocks, [])
        security_groups = try(rule.security_groups, [])
        description = try(rule.description, null)
      }]
      egress_rules = [for rule in aws_security_group.alb.egress : {
        from_port   = rule.from_port
        to_port     = rule.to_port
        protocol    = rule.protocol
        cidr_blocks = try(rule.cidr_blocks, [])
        description = try(rule.description, null)
      }]
    }
    ecs_tasks = {
      id          = aws_security_group.ecs_tasks.id
      name        = aws_security_group.ecs_tasks.name
      description = aws_security_group.ecs_tasks.description
      ingress_rules = [for rule in aws_security_group.ecs_tasks.ingress : {
        from_port   = rule.from_port
        to_port     = rule.to_port
        protocol    = rule.protocol
        cidr_blocks = try(rule.cidr_blocks, [])
        security_groups = try(rule.security_groups, [])
        description = try(rule.description, null)
      }]
      egress_rules = [for rule in aws_security_group.ecs_tasks.egress : {
        from_port   = rule.from_port
        to_port     = rule.to_port
        protocol    = rule.protocol
        cidr_blocks = try(rule.cidr_blocks, [])
        description = try(rule.description, null)
      }]
    }
  }
}

output "scaling_policies" {
  description = "Structured metadata about autoscaling policies"
  value = var.enable_autoscaling ? {
    cpu = {
      arn          = aws_appautoscaling_policy.ecs_cpu[0].arn
      name         = aws_appautoscaling_policy.ecs_cpu[0].name
      target_value = aws_appautoscaling_policy.ecs_cpu[0].target_tracking_scaling_policy_configuration[0].target_value
      metric_type  = aws_appautoscaling_policy.ecs_cpu[0].target_tracking_scaling_policy_configuration[0].predefined_metric_specification[0].predefined_metric_type
    }
    memory = {
      arn          = aws_appautoscaling_policy.ecs_memory[0].arn
      name         = aws_appautoscaling_policy.ecs_memory[0].name
      target_value = aws_appautoscaling_policy.ecs_memory[0].target_tracking_scaling_policy_configuration[0].target_value
      metric_type  = aws_appautoscaling_policy.ecs_memory[0].target_tracking_scaling_policy_configuration[0].predefined_metric_specification[0].predefined_metric_type
    }
  } : {}
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app.name
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "autoscaling_target_id" {
  description = "ID of the auto scaling target"
  value       = var.enable_autoscaling ? aws_appautoscaling_target.ecs[0].id : null
}
