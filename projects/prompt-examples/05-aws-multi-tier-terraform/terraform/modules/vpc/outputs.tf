# ==============================================================================
# VPC MODULE - OUTPUTS
# ==============================================================================
#
# PURPOSE:
# Export VPC resource identifiers and metadata for use by:
# - Parent Terraform configuration
# - Other modules (security groups, ALB, ASG, RDS, etc.)
# - External systems via terraform_remote_state
# - Documentation and troubleshooting
#
# OUTPUT ORGANIZATION:
# 1. VPC Identifiers
# 2. Subnet IDs and CIDRs
# 3. Route Table IDs
# 4. NAT Gateway IDs and IPs
# 5. Internet Gateway ID
# 6. VPC Endpoint IDs
# 7. Network Metadata
#
# ==============================================================================

# ------------------------------------------------------------------------------
# VPC IDENTIFIERS
# ------------------------------------------------------------------------------

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_arn" {
  description = "ARN of the VPC"
  value       = aws_vpc.main.arn
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

# ------------------------------------------------------------------------------
# SUBNET IDS
# ------------------------------------------------------------------------------

output "public_subnet_ids" {
  description = <<-EOT
    List of public subnet IDs.

    USE CASES:
    - Deploy internet-facing Application Load Balancers
    - Create NAT Gateways
    - Launch bastion hosts
    - Deploy VPN servers

    EXAMPLE:
    resource "aws_lb" "public" {
      subnets = module.vpc.public_subnet_ids
      # ALB spans all public subnets across all AZs
    }

    FORMAT:
    ["subnet-abc123", "subnet-def456", "subnet-ghi789"]
    One subnet per AZ specified in var.availability_zones
  EOT
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = <<-EOT
    List of private subnet IDs.

    USE CASES:
    - Deploy application servers (EC2, ECS, EKS)
    - Create internal load balancers
    - Deploy Lambda functions in VPC
    - Run batch processing workloads

    EXAMPLE:
    resource "aws_autoscaling_group" "app" {
      vpc_zone_identifier = module.vpc.private_subnet_ids
      # ASG distributes instances across all private subnets (all AZs)
    }

    ROUTING:
    Private subnets route internet traffic through NAT Gateway
    (outbound only, no inbound from internet)
  EOT
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = <<-EOT
    List of database subnet IDs.

    USE CASES:
    - Create RDS DB subnet groups
    - Deploy ElastiCache clusters
    - Launch Redshift clusters
    - Deploy DocumentDB or Neptune

    EXAMPLE:
    resource "aws_db_subnet_group" "main" {
      subnet_ids = module.vpc.database_subnet_ids
      # RDS can failover between these subnets if Multi-AZ enabled
    }

    ISOLATION:
    Database subnets have NO internet access
    (no NAT Gateway, no Internet Gateway routes)
    Only accessible from private subnets via security groups
  EOT
  value       = var.create_database_subnets ? aws_subnet.database[*].id : []
}

# ------------------------------------------------------------------------------
# SUBNET CIDRS
# ------------------------------------------------------------------------------

output "public_subnet_cidrs" {
  description = <<-EOT
    List of public subnet CIDR blocks.

    USE CASES:
    - Security group rules (allow traffic from public subnets)
    - Network ACL rules
    - Route53 health checks (source IPs)
    - Documentation and diagrams

    EXAMPLE:
    ingress {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = module.vpc.public_subnet_cidrs
      description = "HTTPS from public subnets"
    }
  EOT
  value       = aws_subnet.public[*].cidr_block
}

output "private_subnet_cidrs" {
  description = <<-EOT
    List of private subnet CIDR blocks.

    USE CASES:
    - Security group rules (allow traffic from app tier)
    - Database security groups (allow from app subnets only)
    - Network ACL rules

    EXAMPLE:
    # Database security group
    ingress {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = module.vpc.private_subnet_cidrs
      description = "PostgreSQL from application tier"
    }
  EOT
  value       = aws_subnet.private[*].cidr_block
}

output "database_subnet_cidrs" {
  description = "List of database subnet CIDR blocks"
  value       = var.create_database_subnets ? aws_subnet.database[*].cidr_block : []
}

# ------------------------------------------------------------------------------
# AVAILABILITY ZONES
# ------------------------------------------------------------------------------

output "availability_zones" {
  description = <<-EOT
    List of availability zones where subnets are created.

    USE CASES:
    - Validate subnet placement
    - Documentation
    - Multi-AZ resource planning

    SAME AS INPUT:
    This outputs var.availability_zones for convenience
    (allows downstream modules to know which AZs are used)
  EOT
  value       = var.availability_zones
}

output "public_subnet_azs" {
  description = <<-EOT
    Map of public subnet IDs to their availability zones.

    FORMAT:
    {
      "subnet-abc123" = "us-east-1a"
      "subnet-def456" = "us-east-1b"
      "subnet-ghi789" = "us-east-1c"
    }

    USE CASES:
    - Determine which AZ a subnet is in
    - AZ-specific resource placement
    - Troubleshooting network topology
  EOT
  value       = zipmap(aws_subnet.public[*].id, aws_subnet.public[*].availability_zone)
}

output "private_subnet_azs" {
  description = "Map of private subnet IDs to their availability zones"
  value       = zipmap(aws_subnet.private[*].id, aws_subnet.private[*].availability_zone)
}

output "database_subnet_azs" {
  description = "Map of database subnet IDs to their availability zones"
  value       = var.create_database_subnets ? zipmap(aws_subnet.database[*].id, aws_subnet.database[*].availability_zone) : {}
}

# ------------------------------------------------------------------------------
# ROUTE TABLE IDS
# ------------------------------------------------------------------------------

output "public_route_table_id" {
  description = <<-EOT
    ID of the public route table.

    USE CASES:
    - Add custom routes (VPN, Transit Gateway, VPC Peering)
    - Troubleshoot routing issues
    - Documentation

    ROUTES:
    - VPC CIDR → local (automatic)
    - 0.0.0.0/0 → Internet Gateway

    EXAMPLE (add VPN route):
    resource "aws_route" "vpn" {
      route_table_id         = module.vpc.public_route_table_id
      destination_cidr_block = "192.168.0.0/16"
      gateway_id             = aws_vpn_gateway.main.id
    }
  EOT
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = <<-EOT
    List of private route table IDs (one per AZ).

    WHY MULTIPLE ROUTE TABLES:
    Each private subnet has its own route table to route to
    NAT Gateway in same AZ (high availability).

    FORMAT:
    ["rtb-abc123", "rtb-def456", "rtb-ghi789"]
    One route table per AZ

    USE CASES:
    - Add custom routes per AZ
    - Troubleshoot NAT Gateway routing
    - VPC peering or Transit Gateway routes

    ROUTES (typical):
    - VPC CIDR → local
    - 0.0.0.0/0 → NAT Gateway (in same AZ)
  EOT
  value       = aws_route_table.private[*].id
}

output "database_route_table_id" {
  description = <<-EOT
    ID of the database route table.

    ISOLATION:
    Database route table has NO internet routes
    (no NAT Gateway, no Internet Gateway)

    ROUTES:
    - VPC CIDR → local (only route)

    USE CASES:
    - Add VPC endpoint routes (S3, DynamoDB)
    - VPC peering (database-to-database replication)
    - Verify isolation (no 0.0.0.0/0 route)
  EOT
  value       = var.create_database_subnets ? aws_route_table.database[0].id : null
}

# ------------------------------------------------------------------------------
# NAT GATEWAY INFORMATION
# ------------------------------------------------------------------------------

output "nat_gateway_ids" {
  description = <<-EOT
    List of NAT Gateway IDs.

    MULTI-AZ MODE:
    ["nat-abc123", "nat-def456", "nat-ghi789"]
    One NAT Gateway per AZ

    SINGLE MODE:
    ["nat-abc123"]
    One NAT Gateway total

    USE CASES:
    - Monitor NAT Gateway metrics (CloudWatch)
    - Troubleshoot outbound connectivity
    - Cost allocation
    - Documentation

    CLOUDWATCH METRICS:
    - BytesInFromSource
    - BytesOutToDestination
    - PacketsInFromSource
    - PacketsOutToDestination
    - ErrorPortAllocation (indicates exhaustion)
  EOT
  value       = var.enable_nat_gateway ? (var.single_nat_gateway ? aws_nat_gateway.single[*].id : aws_nat_gateway.main[*].id) : []
}

output "nat_gateway_public_ips" {
  description = <<-EOT
    List of Elastic IPs attached to NAT Gateways.

    WHAT THESE IPs REPRESENT:
    These are the public IP addresses that outbound traffic from
    private subnets appears to come from.

    USE CASES:

    1. EXTERNAL API WHITELISTING:
       If external service requires IP whitelisting:
       - Provide these IPs to vendor
       - All traffic from private subnets uses these IPs

       Example: Stripe API whitelisting
       → Add NAT Gateway IPs to Stripe dashboard

    2. FIREWALL RULES:
       Corporate firewall may need to allow these IPs
       for accessing on-premises resources via VPN

    3. LOGGING:
       External services log traffic from these IPs
       Useful for troubleshooting ("Did request come from us?")

    4. DOCUMENTATION:
       Include in architecture docs and runbooks

    FORMAT:
    MULTI-AZ: ["54.123.45.67", "18.234.56.78", "3.210.98.76"]
    SINGLE: ["54.123.45.67"]

    STATIC IPs:
    These are Elastic IPs (static, don't change unless you destroy NAT Gateway)

    COST:
    - While attached: FREE
    - While detached: $0.005/hour (~$3.60/month)
    - Always keep attached or release!
  EOT
  value       = var.enable_nat_gateway ? (var.single_nat_gateway ? aws_eip.nat_single[*].public_ip : aws_eip.nat[*].public_ip) : []
}

# ------------------------------------------------------------------------------
# INTERNET GATEWAY
# ------------------------------------------------------------------------------

output "internet_gateway_id" {
  description = <<-EOT
    ID of the Internet Gateway.

    USE CASES:
    - Add routes to custom route tables
    - Troubleshoot public subnet connectivity
    - Documentation

    INTERNET GATEWAY:
    - Provides bidirectional internet access for public subnets
    - AWS-managed (no configuration needed)
    - Horizontally scaled, redundant, HA
    - Free (no hourly charges)
  EOT
  value       = aws_internet_gateway.main.id
}

# ------------------------------------------------------------------------------
# VPC ENDPOINTS
# ------------------------------------------------------------------------------

output "s3_vpc_endpoint_id" {
  description = <<-EOT
    ID of the S3 VPC endpoint (if enabled).

    S3 ENDPOINT BENEFITS:
    - Private connection to S3 (traffic stays in AWS network)
    - No NAT Gateway fees for S3 traffic ($0.045/GB savings)
    - Better performance (lower latency)
    - Free (gateway endpoint)

    USE CASES:
    - Verify endpoint is attached to route tables
    - Troubleshoot S3 connectivity from private subnets
    - Documentation

    NULL IF DISABLED:
    Returns null if var.enable_s3_endpoint = false
  EOT
  value       = var.enable_s3_endpoint ? aws_vpc_endpoint.s3[0].id : null
}

output "dynamodb_vpc_endpoint_id" {
  description = <<-EOT
    ID of the DynamoDB VPC endpoint (if enabled).

    Similar benefits to S3 endpoint:
    - Private connection to DynamoDB
    - No NAT Gateway fees
    - Free gateway endpoint

    NULL IF DISABLED:
    Returns null if var.enable_dynamodb_endpoint = false
  EOT
  value       = var.enable_dynamodb_endpoint ? aws_vpc_endpoint.dynamodb[0].id : null
}

# ------------------------------------------------------------------------------
# VPC FLOW LOGS
# ------------------------------------------------------------------------------

output "flow_log_id" {
  description = <<-EOT
    ID of the VPC Flow Log (if enabled).

    USE CASES:
    - Monitor flow log status
    - Troubleshoot logging issues
    - Verify logs are being captured

    NULL IF DISABLED:
    Returns null if var.enable_flow_logs = false
  EOT
  value       = var.enable_flow_logs ? aws_flow_log.main[0].id : null
}

output "flow_log_cloudwatch_log_group_name" {
  description = <<-EOT
    CloudWatch Log Group name for flow logs (if using CloudWatch destination).

    USE CASES:
    - Query logs with CloudWatch Insights
    - Create metric filters
    - Set up alarms based on log patterns
    - Troubleshoot using CloudWatch console

    NULL IF:
    - var.enable_flow_logs = false
    - var.flow_log_destination_type = "s3"

    EXAMPLE QUERY (CloudWatch Insights):
    fields @timestamp, srcaddr, dstaddr, dstport, action
    | filter dstport = 22 and action = "REJECT"
    | stats count() by srcaddr
    | sort count desc
    | limit 20

    This finds top 20 source IPs trying to SSH (rejected)
  EOT
  value       = var.enable_flow_logs && var.flow_log_destination_type == "cloud-watch-logs" ? aws_cloudwatch_log_group.flow_log[0].name : null
}

# ------------------------------------------------------------------------------
# NETWORK METADATA
# ------------------------------------------------------------------------------

output "vpc_enable_dns_support" {
  description = <<-EOT
    Whether DNS support is enabled for the VPC.

    TRUE:
    - AWS DNS resolver available at VPC CIDR + 2
    - VPC endpoints work correctly
    - Route53 private zones work

    USE CASES:
    - Validation
    - Documentation
    - Troubleshooting DNS issues
  EOT
  value       = aws_vpc.main.enable_dns_support
}

output "vpc_enable_dns_hostnames" {
  description = <<-EOT
    Whether DNS hostnames are enabled for the VPC.

    TRUE:
    - Instances with public IPs get DNS names
    - RDS endpoints work correctly
    - ElastiCache endpoints work

    USE CASES:
    - Validation
    - Documentation
    - Troubleshooting connectivity
  EOT
  value       = aws_vpc.main.enable_dns_hostnames
}

output "vpc_main_route_table_id" {
  description = <<-EOT
    ID of the VPC's main route table.

    MAIN ROUTE TABLE:
    - Default route table for subnets without explicit association
    - We create custom route tables and associate explicitly
    - Main route table usually remains unused (best practice)

    WHY NOT USE MAIN ROUTE TABLE:
    - Explicit associations are clearer (easier to understand)
    - Avoid accidental use by new subnets
    - Better organization

    USE CASES:
    - Verify no subnets using main route table
    - Documentation
    - Troubleshooting
  EOT
  value       = aws_vpc.main.main_route_table_id
}

# ------------------------------------------------------------------------------
# SUMMARY OUTPUTS (CONVENIENCE)
# ------------------------------------------------------------------------------

output "vpc_summary" {
  description = <<-EOT
    Summary of VPC configuration for easy reference.

    USE CASES:
    - Quick reference in Terraform output
    - Documentation generation
    - Troubleshooting

    EXAMPLE OUTPUT:
    {
      vpc_id              = "vpc-abc123"
      vpc_cidr            = "10.0.0.0/16"
      availability_zones  = ["us-east-1a", "us-east-1b", "us-east-1c"]
      public_subnets      = 3
      private_subnets     = 3
      database_subnets    = 3
      nat_gateways        = 3
      nat_mode            = "multi-az"
    }
  EOT
  value = {
    vpc_id             = aws_vpc.main.id
    vpc_cidr           = aws_vpc.main.cidr_block
    availability_zones = var.availability_zones
    public_subnets     = length(aws_subnet.public)
    private_subnets    = length(aws_subnet.private)
    database_subnets   = var.create_database_subnets ? length(aws_subnet.database) : 0
    nat_gateways       = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0
    nat_mode           = var.enable_nat_gateway ? (var.single_nat_gateway ? "single" : "multi-az") : "none"
    flow_logs_enabled  = var.enable_flow_logs
    s3_endpoint        = var.enable_s3_endpoint
    dynamodb_endpoint  = var.enable_dynamodb_endpoint
  }
}

# Complete outputs.tf with all VPC resource identifiers
# This demonstrates the exhaustive documentation pattern for module outputs
