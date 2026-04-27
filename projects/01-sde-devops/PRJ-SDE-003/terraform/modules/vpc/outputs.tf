# VPC Module Outputs
# Purpose: Export VPC resource IDs and attributes for use by other modules
# Usage: Other modules reference these values via module.vpc.vpc_id, etc.
#
# Output Design:
# - Include all resource IDs that other modules need
# - Provide both individual and list outputs for flexibility
# - Add descriptions explaining what each output contains and how to use it
# - Mark sensitive outputs appropriately

# Core VPC Outputs

output "vpc_id" {
  description = "ID of the VPC. Use this to attach resources to the VPC or create VPC-specific resources."
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC. Useful for security group rules and network calculations."
  value       = aws_vpc.main.cidr_block
}

output "vpc_arn" {
  description = "ARN of the VPC. Required for some IAM policies and resource-based policies."
  value       = aws_vpc.main.arn
}

# Subnet Outputs

output "public_subnet_ids" {
  description = <<-EOT
    List of public subnet IDs (one per AZ).
    Use for: ALB, NAT Gateways, Bastion hosts, or any resource needing direct internet access.
    Example: module.vpc.public_subnet_ids[0] for first AZ
  EOT
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = <<-EOT
    List of private application subnet IDs (one per AZ).
    Use for: EC2 instances, ECS tasks, Lambda functions, or application tier resources.
    These subnets have internet access via NAT Gateway but no inbound internet access.
  EOT
  value       = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  description = <<-EOT
    List of private database subnet IDs (one per AZ).
    Use for: RDS instances, ElastiCache, Redshift, or any database tier resources.
    These subnets are completely isolated (no internet access even outbound).
  EOT
  value       = aws_subnet.private_db[*].id
}

output "public_subnet_cidrs" {
  description = "CIDR blocks of public subnets. Useful for security group source rules."
  value       = aws_subnet.public[*].cidr_block
}

output "private_app_subnet_cidrs" {
  description = "CIDR blocks of private app subnets. Useful for security group source rules."
  value       = aws_subnet.private_app[*].cidr_block
}

output "private_db_subnet_cidrs" {
  description = "CIDR blocks of private DB subnets. Useful for database security group rules."
  value       = aws_subnet.private_db[*].cidr_block
}

# Individual subnet IDs for specific AZ targeting

output "public_subnet_az1" {
  description = "Public subnet ID in first availability zone."
  value       = length(aws_subnet.public) > 0 ? aws_subnet.public[0].id : null
}

output "public_subnet_az2" {
  description = "Public subnet ID in second availability zone."
  value       = length(aws_subnet.public) > 1 ? aws_subnet.public[1].id : null
}

output "public_subnet_az3" {
  description = "Public subnet ID in third availability zone."
  value       = length(aws_subnet.public) > 2 ? aws_subnet.public[2].id : null
}

# Availability Zone Information

output "availability_zones" {
  description = "List of availability zones used in VPC. Matches order of subnet lists."
  value       = local.availability_zones
}

output "azs_count" {
  description = "Number of availability zones used. Useful for count-based resource creation."
  value       = length(local.availability_zones)
}

# Gateway Outputs

output "internet_gateway_id" {
  description = "ID of the Internet Gateway. Rarely needed by other modules."
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = <<-EOT
    List of NAT Gateway IDs (one per AZ if HA enabled, otherwise single NAT).
    Useful for: Custom route tables, monitoring NAT Gateway metrics.
  EOT
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = <<-EOT
    Public IP addresses of NAT Gateways.
    Use for: Whitelisting in external APIs, firewall rules, logging/monitoring.
    These are the IPs that external services see for requests from private subnets.
  EOT
  value       = aws_eip.nat[*].public_ip
}

# Route Table Outputs

output "public_route_table_id" {
  description = "ID of the public route table. Has route to Internet Gateway."
  value       = aws_route_table.public.id
}

output "private_app_route_table_ids" {
  description = <<-EOT
    List of private application route table IDs.
    One per AZ if NAT HA enabled, otherwise single route table for all AZs.
  EOT
  value       = aws_route_table.private_app[*].id
}

output "private_db_route_table_ids" {
  description = "List of private database route table IDs (one per AZ, no internet routes)."
  value       = aws_route_table.private_db[*].id
}

# VPC Endpoint Outputs

output "s3_vpc_endpoint_id" {
  description = "ID of S3 VPC endpoint (if enabled). Use for endpoint policies or monitoring."
  value       = length(aws_vpc_endpoint.s3) > 0 ? aws_vpc_endpoint.s3[0].id : null
}

output "dynamodb_vpc_endpoint_id" {
  description = "ID of DynamoDB VPC endpoint (if enabled)."
  value       = length(aws_vpc_endpoint.dynamodb) > 0 ? aws_vpc_endpoint.dynamodb[0].id : null
}

output "vpc_endpoint_sg_id" {
  description = <<-EOT
    Security group ID for VPC interface endpoints (ECR, SSM, Secrets Manager).
    Use this SG as source in other security groups to allow traffic from VPC endpoints.
  EOT
  value       = length(aws_security_group.vpc_endpoints) > 0 ? aws_security_group.vpc_endpoints[0].id : null
}

# Flow Logs Outputs

output "flow_log_id" {
  description = "ID of VPC Flow Log (if enabled)."
  value       = length(aws_flow_log.main) > 0 ? aws_flow_log.main[0].id : null
}

output "flow_log_cloudwatch_log_group" {
  description = "CloudWatch Log Group name for VPC Flow Logs. Use for CloudWatch Insights queries."
  value       = length(aws_cloudwatch_log_group.flow_logs) > 0 ? aws_cloudwatch_log_group.flow_logs[0].name : null
}

# Default Security Group (for reference, should be restricted)

output "default_security_group_id" {
  description = <<-EOT
    ID of the VPC's default security group.
    WARNING: Best practice is to NEVER use default SG. Always create specific security groups.
    This output exists for auditing/compliance purposes.
  EOT
  value       = aws_vpc.main.default_security_group_id
}

# Network ACL Outputs

output "default_network_acl_id" {
  description = "ID of the default network ACL. Useful for compliance auditing."
  value       = aws_vpc.main.default_network_acl_id
}

# Calculated Outputs for Convenience

output "nat_gateway_count" {
  description = "Number of NAT Gateways created (0, 1, or 3 depending on configuration)."
  value       = local.nat_gateway_count
}

output "subnet_count_by_type" {
  description = "Count of subnets by type. Useful for validation and debugging."
  value = {
    public      = length(aws_subnet.public)
    private_app = length(aws_subnet.private_app)
    private_db  = length(aws_subnet.private_db)
  }
}

# Summary Output for Documentation/Verification

output "vpc_summary" {
  description = <<-EOT
    Human-readable summary of VPC configuration.
    Use in terraform output for quick verification after deployment.
  EOT
  value = {
    vpc_id            = aws_vpc.main.id
    vpc_cidr          = aws_vpc.main.cidr_block
    azs               = local.availability_zones
    nat_gateways      = length(aws_nat_gateway.main)
    public_subnets    = length(aws_subnet.public)
    private_subnets   = length(aws_subnet.private_app)
    database_subnets  = length(aws_subnet.private_db)
    flow_logs_enabled = var.enable_flow_logs
    s3_endpoint       = var.enable_s3_endpoint
    ssm_endpoints     = var.enable_ssm_endpoints
  }
}
