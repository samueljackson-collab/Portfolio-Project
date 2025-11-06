# Root Terraform Outputs for SIEM Pipeline

#------------------------------------------------------------------------------
# OpenSearch Outputs
#------------------------------------------------------------------------------

output "opensearch_domain_name" {
  description = "Name of the OpenSearch domain"
  value       = module.opensearch.domain_name
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = module.opensearch.domain_endpoint
}

output "opensearch_dashboard_url" {
  description = "URL to access OpenSearch Dashboards"
  value       = module.opensearch.dashboard_url
}

output "opensearch_kibana_endpoint" {
  description = "OpenSearch Dashboards endpoint"
  value       = module.opensearch.kibana_endpoint
}

#------------------------------------------------------------------------------
# Kinesis Firehose Outputs
#------------------------------------------------------------------------------

output "firehose_delivery_stream_name" {
  description = "Name of the Kinesis Firehose delivery stream"
  value       = module.kinesis_firehose.delivery_stream_name
}

output "lambda_function_name" {
  description = "Name of the Lambda log transformer function"
  value       = module.kinesis_firehose.lambda_function_name
}

output "backup_bucket_name" {
  description = "S3 bucket for failed log records"
  value       = module.kinesis_firehose.backup_bucket_name
}

#------------------------------------------------------------------------------
# Security Outputs
#------------------------------------------------------------------------------

output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = var.enable_guardduty ? aws_guardduty_detector.main[0].id : null
}

output "cloudtrail_name" {
  description = "CloudTrail trail name"
  value       = var.enable_cloudtrail ? aws_cloudtrail.main[0].name : null
}

output "cloudtrail_bucket_name" {
  description = "S3 bucket for CloudTrail logs"
  value       = var.enable_cloudtrail ? aws_s3_bucket.cloudtrail[0].id : null
}

#------------------------------------------------------------------------------
# Alerting Outputs
#------------------------------------------------------------------------------

output "security_alerts_topic_arn" {
  description = "SNS topic ARN for security alerts"
  value       = aws_sns_topic.security_alerts.arn
}

#------------------------------------------------------------------------------
# Log Groups
#------------------------------------------------------------------------------

output "log_groups" {
  description = "CloudWatch log groups for all components"
  value = {
    guardduty          = var.enable_guardduty ? aws_cloudwatch_log_group.guardduty[0].name : null
    cloudtrail         = var.enable_cloudtrail ? aws_cloudwatch_log_group.cloudtrail[0].name : null
    lambda_transformer = module.kinesis_firehose.lambda_log_group_name
    firehose           = module.kinesis_firehose.firehose_log_group_name
    opensearch         = module.opensearch.log_group_names
  }
}

#------------------------------------------------------------------------------
# Deployment Summary
#------------------------------------------------------------------------------

output "deployment_summary" {
  description = "Summary of deployed SIEM infrastructure"
  value = {
    region              = var.aws_region
    project_name        = var.project_name
    environment         = var.environment
    opensearch_nodes    = var.opensearch_instance_count
    opensearch_version  = var.opensearch_engine_version
    guardduty_enabled   = var.enable_guardduty
    cloudtrail_enabled  = var.enable_cloudtrail
    alert_email         = var.alert_email != "" ? "configured" : "not configured"
  }
}

output "next_steps" {
  description = "Post-deployment instructions"
  value       = <<-EOT

  ✅ SIEM Pipeline deployed successfully!

  🔍 OpenSearch Dashboards:
  ${module.opensearch.dashboard_url}
  Username: ${var.opensearch_master_user}
  Password: [Securely stored]

  📊 Components Deployed:
  - OpenSearch Cluster: ${var.opensearch_instance_count} nodes
  - GuardDuty: ${var.enable_guardduty ? "Enabled" : "Disabled"}
  - CloudTrail: ${var.enable_cloudtrail ? "Enabled" : "Disabled"}
  - Kinesis Firehose: Active
  - Lambda Transformer: ${module.kinesis_firehose.lambda_function_name}

  📋 Next Steps:
  1. Access OpenSearch Dashboards using the URL above
  2. Create index patterns for security-events-*
  3. Import dashboard configurations from /dashboards folder
  4. Configure alert rules and monitors
  5. Subscribe to SNS topic: ${aws_sns_topic.security_alerts.arn}
  ${var.alert_email != "" ? "6. Confirm email subscription for alerts" : "6. Add email subscription for alerts"}
  7. Test log ingestion with sample events
  8. Review CloudWatch alarms in AWS Console

  🔐 Security Recommendations:
  - Store OpenSearch password in AWS Secrets Manager
  - Review and customize alert thresholds
  - Enable additional log sources (VPC Flow Logs, etc.)
  - Configure backup and snapshot policies
  - Set up dashboard access controls
  - Review GuardDuty findings regularly

  📚 Documentation:
  - Project README: ../README.md
  - Lambda Code: ../lambda/log_transformer.py
  - Test Suite: ../lambda/test_log_transformer.py

  🚨 Monitoring:
  - OpenSearch Alarms: ${length(module.opensearch.alarm_names)} configured
  - Firehose Alarms: ${length(module.kinesis_firehose.alarm_names)} configured
  - SNS Alerts: ${aws_sns_topic.security_alerts.name}

  💰 Estimated Monthly Cost:
  - Development: ~$50-100 (t3.small.search, single AZ)
  - Production: ~$200-400 (multi-AZ, dedicated masters)

  EOT
}
