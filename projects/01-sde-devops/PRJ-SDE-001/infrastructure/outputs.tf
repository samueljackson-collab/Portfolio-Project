# Root Terraform Outputs
# These values are displayed after successful terraform apply

#------------------------------------------------------------------------------
# VPC Outputs
#------------------------------------------------------------------------------

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnet_ids
}

output "nat_gateway_ips" {
  description = "NAT Gateway public IPs"
  value       = module.vpc.nat_gateway_ips
}

#------------------------------------------------------------------------------
# Database Outputs
#------------------------------------------------------------------------------

output "database_endpoint" {
  description = "Database connection endpoint"
  value       = module.database.db_endpoint
}

output "database_security_group_id" {
  description = "Security group ID for database access"
  value       = module.database.db_security_group_id
}

output "database_instance_id" {
  description = "RDS instance identifier"
  value       = module.database.db_instance_identifier
}

output "connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = "postgresql://${var.db_username}:PASSWORD@${module.database.db_endpoint}/postgres"
  sensitive   = false
}

#------------------------------------------------------------------------------
# Application Outputs (if deployed)
#------------------------------------------------------------------------------

output "application_url" {
  description = "URL to access the application"
  value       = var.deploy_application ? module.application[0].application_url : "Application not deployed (set deploy_application = true)"
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = var.deploy_application ? module.application[0].alb_dns_name : null
}

output "target_groups" {
  description = "Structured target group outputs for downstream consumers"
  value       = var.deploy_application ? module.application[0].target_groups : {}
}

output "security_groups" {
  description = "Structured security group outputs for downstream consumers"
  value       = var.deploy_application ? module.application[0].security_groups : {}
}

output "scaling_policies" {
  description = "Structured auto scaling policy outputs for downstream consumers"
  value       = var.deploy_application ? module.application[0].scaling_policies : {}
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = var.deploy_application ? module.application[0].ecs_cluster_name : null
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = var.deploy_application ? module.application[0].ecs_service_name : null
}

#------------------------------------------------------------------------------
# Monitoring Outputs
#------------------------------------------------------------------------------

output "cloudwatch_alarms" {
  description = "CloudWatch alarm names for monitoring"
  value = {
    database_cpu = {
      name                 = aws_cloudwatch_metric_alarm.database_cpu.alarm_name
      arn                  = aws_cloudwatch_metric_alarm.database_cpu.arn
      metric_name          = aws_cloudwatch_metric_alarm.database_cpu.metric_name
      namespace            = aws_cloudwatch_metric_alarm.database_cpu.namespace
      threshold            = aws_cloudwatch_metric_alarm.database_cpu.threshold
      comparison_operator  = aws_cloudwatch_metric_alarm.database_cpu.comparison_operator
      evaluation_periods   = aws_cloudwatch_metric_alarm.database_cpu.evaluation_periods
      period               = aws_cloudwatch_metric_alarm.database_cpu.period
      statistic            = aws_cloudwatch_metric_alarm.database_cpu.statistic
    }
    database_storage = {
      name                 = aws_cloudwatch_metric_alarm.database_storage.alarm_name
      arn                  = aws_cloudwatch_metric_alarm.database_storage.arn
      metric_name          = aws_cloudwatch_metric_alarm.database_storage.metric_name
      namespace            = aws_cloudwatch_metric_alarm.database_storage.namespace
      threshold            = aws_cloudwatch_metric_alarm.database_storage.threshold
      comparison_operator  = aws_cloudwatch_metric_alarm.database_storage.comparison_operator
      evaluation_periods   = aws_cloudwatch_metric_alarm.database_storage.evaluation_periods
      period               = aws_cloudwatch_metric_alarm.database_storage.period
      statistic            = aws_cloudwatch_metric_alarm.database_storage.statistic
    }
    database_connections = {
      name                 = aws_cloudwatch_metric_alarm.database_connections.alarm_name
      arn                  = aws_cloudwatch_metric_alarm.database_connections.arn
      metric_name          = aws_cloudwatch_metric_alarm.database_connections.metric_name
      namespace            = aws_cloudwatch_metric_alarm.database_connections.namespace
      threshold            = aws_cloudwatch_metric_alarm.database_connections.threshold
      comparison_operator  = aws_cloudwatch_metric_alarm.database_connections.comparison_operator
      evaluation_periods   = aws_cloudwatch_metric_alarm.database_connections.evaluation_periods
      period               = aws_cloudwatch_metric_alarm.database_connections.period
      statistic            = aws_cloudwatch_metric_alarm.database_connections.statistic
    }
  }
}

output "vpc_flow_logs_group" {
  description = "CloudWatch Log Group for VPC Flow Logs"
  value       = module.vpc.flow_logs_log_group_name
}

output "application_logs_group" {
  description = "CloudWatch Log Group for application logs"
  value       = var.deploy_application ? module.application[0].cloudwatch_log_group_name : null
}

#------------------------------------------------------------------------------
# Deployment Summary
#------------------------------------------------------------------------------

output "deployment_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    region              = var.aws_region
    project_name        = var.project_name
    environment         = var.environment
    vpc_cidr            = var.vpc_cidr
    availability_zones  = var.az_count
    database_deployed   = true
    application_deployed = var.deploy_application
    nat_gateway_ha      = !var.single_nat_gateway
    flow_logs_enabled   = var.enable_flow_logs
  }
}

output "next_steps" {
  description = "Post-deployment instructions"
  value       = var.deploy_application ? <<-EOT

  ✅ Full-stack infrastructure deployed successfully!

  🌐 Application Access:
  ${module.application[0].application_url}

  🗄️ Database Connection:
  Host: ${module.database.db_endpoint}
  Port: 5432
  User: ${var.db_username}
  Database: postgres

  📋 Next Steps:
  1. Access application: ${module.application[0].application_url}
  2. Connect to database from ECS tasks (environment variables configured)
  3. Create application schema: CREATE DATABASE myapp;
  4. Review CloudWatch dashboards and alarms
  5. Configure custom domain (Route53 → ALB)
  6. Set up SSL/TLS certificate (ACM → ALB HTTPS listener)
  7. Review VPC Flow Logs: ${module.vpc.flow_logs_log_group_name}
  8. Configure backup verification procedures

  🔒 Security Recommendations:
  - Store db_password in AWS Secrets Manager
  - Enable deletion_protection for production
  - Enable Multi-AZ for production: db_multi_az = true
  - Review security groups and firewall rules
  - Enable GuardDuty for threat detection
  - Configure AWS WAF on ALB

  📊 Monitoring:
  - Database alarms: ${aws_cloudwatch_metric_alarm.database_cpu.alarm_name}
  - VPC Flow Logs: ${module.vpc.flow_logs_log_group_name}
  - Application logs: ${module.application[0].cloudwatch_log_group_name}
  - Container Insights enabled

  EOT
  : <<-EOT

  ✅ Database infrastructure deployed successfully!

  🗄️ Database Connection:
  Host: ${module.database.db_endpoint}
  Port: 5432
  User: ${var.db_username}
  Database: postgres

  📋 Next Steps:
  1. Deploy application: Set deploy_application = true in terraform.tfvars
  2. Connect to database from application in private subnets
  3. Create application schema: CREATE DATABASE myapp;
  4. Configure monitoring alerts (CloudWatch alarms created)
  5. Set up backup verification procedures
  6. Review security group rules: ${module.database.db_security_group_id}

  🔒 Security Recommendations:
  - Store db_password in AWS Secrets Manager
  - Enable deletion_protection for production
  - Enable Multi-AZ for production: db_multi_az = true
  - Review VPC Flow Logs: ${module.vpc.flow_logs_log_group_name}

  📊 Monitoring:
  - Database alarms configured
  - VPC Flow Logs: ${module.vpc.flow_logs_log_group_name}

  EOT
}
