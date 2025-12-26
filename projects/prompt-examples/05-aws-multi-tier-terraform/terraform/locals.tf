# ==============================================================================
# TERRAFORM LOCAL VALUES
# ==============================================================================
#
# PURPOSE:
# Local values allow you to assign names to expressions and reuse them throughout
# your configuration without repeating the same logic multiple times.
#
# LOCALS VS VARIABLES:
#
# VARIABLES (var.xxx):
# - Input from user (terraform.tfvars, -var flags, environment variables)
# - Can be overridden per environment
# - Examples: var.project_name, var.environment, var.aws_region
# - Use when: Value should be configurable by user
#
# LOCALS (local.xxx):
# - Computed within Terraform configuration
# - Cannot be overridden externally (internal to the configuration)
# - Examples: local.name_prefix, local.common_tags, local.azs
# - Use when: Value is derived from other values or constant across environments
#
# EXAMPLE SHOWING THE DIFFERENCE:
#
# variable "project_name" {
#   # User provides this (changeable)
# }
#
# locals {
#   name_prefix = "${var.project_name}-${var.environment}"  # Computed from variables
#   # Always constructed the same way, not directly configurable
# }
#
# WHY USE LOCALS:
#
# 1. DRY (DON'T REPEAT YOURSELF):
#    Without locals:
#    resource "aws_vpc" "main" {
#      tags = {
#        Name        = "${var.project_name}-${var.environment}-vpc"
#        Environment = var.environment
#        ManagedBy   = "terraform"
#      }
#    }
#    resource "aws_subnet" "public" {
#      tags = {
#        Name        = "${var.project_name}-${var.environment}-public-subnet"
#        Environment = var.environment
#        ManagedBy   = "terraform"
#      }
#    }
#    # Repeated tags in every resource!
#
#    With locals:
#    locals {
#      common_tags = {
#        Environment = var.environment
#        ManagedBy   = "terraform"
#      }
#    }
#    resource "aws_vpc" "main" {
#      tags = merge(local.common_tags, { Name = "${local.name_prefix}-vpc" })
#    }
#    resource "aws_subnet" "public" {
#      tags = merge(local.common_tags, { Name = "${local.name_prefix}-public-subnet" })
#    }
#
# 2. READABILITY:
#    Complex expressions become named values:
#    Bad:  cidr = cidrsubnet(var.vpc_cidr, 4, count.index)
#    Good: cidr = local.public_subnet_cidrs[count.index]
#
# 3. CONSISTENCY:
#    Ensures same logic used everywhere:
#    local.name_prefix always constructs names the same way
#
# 4. CONDITIONAL LOGIC:
#    Environment-specific values without duplicating code:
#    local.instance_count = var.environment == "prod" ? 3 : 1
#
# ==============================================================================

locals {
  # NAME PREFIX
  #
  # Standard prefix for all resource names.
  # Format: {project_name}-{environment}
  # Example: myapp-prod
  #
  # USAGE:
  # resource "aws_vpc" "main" {
  #   tags = { Name = "${local.name_prefix}-vpc" }  # Results in: myapp-prod-vpc
  # }
  #
  # WHY CENTRALIZE NAMING:
  # - Consistency (all resources named the same way)
  # - Easy to change format (update in one place)
  # - Searchability (grep for myapp-prod to find all resources)
  # - Cost tracking (filter billing by resource name prefix)
  #
  # NAMING BEST PRACTICES:
  # - Include project name (identify which application)
  # - Include environment (separate dev from prod resources)
  # - Use hyphens (not underscores) for AWS compatibility
  # - Keep short (some resources have name length limits)
  # - Lowercase only (some resources require lowercase)
  #
  name_prefix = "${var.project_name}-${var.environment}"

  # AVAILABILITY ZONES
  #
  # List of availability zones to use for multi-AZ resources.
  #
  # DYNAMIC AZ SELECTION:
  # Instead of hardcoding AZs (["us-east-1a", "us-east-1b", "us-east-1c"]),
  # we dynamically select the first N AZs from the region.
  #
  # WHY DYNAMIC:
  # - Works in any region (no hardcoded AZ names)
  # - Adapts to regions with different number of AZs
  # - Can easily change number of AZs (var.azs_count)
  #
  # HOW IT WORKS:
  # 1. data.aws_availability_zones.available (see data.tf) gets all available AZs
  # 2. Take first var.azs_count AZs from the list
  # 3. Example: var.azs_count = 3 → ["us-east-1a", "us-east-1b", "us-east-1c"]
  #
  # SLICING SYNTAX:
  # slice(list, start_index, end_index)
  # slice([a,b,c,d,e], 0, 3) → [a,b,c]
  #
  # EXAMPLE OUTPUT:
  # In us-east-1 with azs_count = 3:
  # local.azs = ["us-east-1a", "us-east-1b", "us-east-1c"]
  #
  # USAGE:
  # module "vpc" {
  #   azs = local.azs
  #   # VPC module creates subnets in these 3 AZs
  # }
  #
  # resource "aws_subnet" "public" {
  #   count             = length(local.azs)  # Creates 3 subnets
  #   availability_zone = local.azs[count.index]  # One per AZ
  #   # ...
  # }
  #
  # AZ ORDERING:
  # AWS returns AZs in alphabetical order: us-east-1a, us-east-1b, us-east-1c, ...
  # Taking first N ensures consistent selection across applies.
  #
  # REGIONAL DIFFERENCES:
  # - us-east-1 has 6 AZs (a, b, c, d, e, f)
  # - ap-northeast-1 has 4 AZs (a, c, d)
  # - eu-south-1 has 3 AZs (a, b, c)
  #
  # Dynamic selection handles this automatically.
  #
  azs = slice(data.aws_availability_zones.available.names, 0, var.azs_count)

  # COMMON TAGS
  #
  # Tags applied to all resources (merged with resource-specific tags).
  #
  # WHY TAG EVERYTHING:
  # 1. COST TRACKING:
  #    Filter AWS Cost Explorer by tags:
  #    - Show costs for Environment:prod vs Environment:dev
  #    - Show costs for Project:myapp
  #    - Show costs for CostCenter:engineering
  #
  # 2. RESOURCE ORGANIZATION:
  #    In AWS Console, filter resources by tags:
  #    - Show all prod resources: Filter by Environment:prod
  #    - Show all resources for a project: Filter by Project:myapp
  #
  # 3. AUTOMATION:
  #    Scripts can filter resources by tags:
  #    ```bash
  #    # Stop all dev EC2 instances (save money overnight)
  #    aws ec2 stop-instances \
  #      --instance-ids $(aws ec2 describe-instances \
  #        --filters "Name=tag:Environment,Values=dev" \
  #        --query 'Reservations[].Instances[].InstanceId' \
  #        --output text)
  #    ```
  #
  # 4. COMPLIANCE:
  #    Many compliance frameworks require tagging:
  #    - Who owns this resource? (Owner tag)
  #    - What's it used for? (Purpose tag)
  #    - When can we delete it? (ExpirationDate tag for temporary resources)
  #
  # 5. SECURITY:
  #    IAM policies can enforce tagging:
  #    - Deny resource creation without required tags
  #    - Restrict access based on tags (developers can only access dev resources)
  #
  # STANDARD TAG SET:
  #
  # Environment: dev, staging, prod
  # - Use case: Cost allocation, automation, access control
  #
  # Project: Project or application name
  # - Use case: Cost tracking across multiple applications
  #
  # ManagedBy: terraform, cloudformation, manual, etc.
  # - Use case: Know which resources are safe to import into IaC
  # - If ManagedBy:terraform, expect this resource to be in Terraform state
  # - If ManagedBy:manual, don't import (someone created in console)
  #
  # OPTIONAL TAGS TO CONSIDER:
  # - Owner: team or individual responsible (john@example.com, platform-team)
  # - CostCenter: Finance cost center code (CC-123, ENG-001)
  # - Compliance: HIPAA, PCI-DSS, SOC2, etc.
  # - BackupPolicy: daily, weekly, none
  # - DataClassification: public, internal, confidential, restricted
  # - ExpirationDate: 2024-12-31 (for temporary resources)
  # - ServiceName: api, web, worker, database
  # - Version: v1.2.3 (application version)
  #
  # USAGE:
  # resource "aws_vpc" "main" {
  #   tags = merge(
  #     local.common_tags,
  #     {
  #       Name    = "${local.name_prefix}-vpc"
  #       Purpose = "main-vpc-for-multi-tier-app"
  #     }
  #   )
  # }
  #
  # MERGE FUNCTION:
  # merge(map1, map2) combines two maps:
  # merge({a=1, b=2}, {b=3, c=4}) → {a=1, b=3, c=4}
  # Later maps override earlier maps for duplicate keys.
  #
  # TAG ENFORCEMENT:
  # AWS Tag Policies can require tags:
  # ```json
  # {
  #   "tags": {
  #     "Environment": {
  #       "tag_key": {"@@assign": "Environment"},
  #       "tag_value": {"@@assign": ["dev", "staging", "prod"]},
  #       "enforced_for": {"@@assign": ["ec2:*", "rds:*", "s3:*"]}
  #     }
  #   }
  # }
  # ```
  #
  # COST ALLOCATION TAGS:
  # In AWS Billing console, activate cost allocation tags:
  # 1. Billing → Cost Allocation Tags
  # 2. Select tags to activate (Environment, Project, Owner, etc.)
  # 3. Wait 24 hours for tags to appear in Cost Explorer
  # 4. Filter costs by these tags
  #
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }

  # ENVIRONMENT-SPECIFIC CONFIGURATION
  #
  # Different values based on environment without if/else in every resource.
  #
  # INSTANCE COUNTS:
  # Fewer instances in dev (save money), more in prod (handle load).
  #
  # WHY NOT HARDCODE IN VARIABLES:
  # Could use variables with different default per environment:
  # var.instance_count = 3  # In prod.tfvars
  # var.instance_count = 1  # In dev.tfvars
  #
  # But this requires:
  # - Separate tfvars file per environment (more files to maintain)
  # - Risk of forgetting to set value (terraform uses default)
  #
  # With locals, logic is in one place:
  # local.instance_count = var.environment == "prod" ? 3 : 1
  # - Single source of truth
  # - No separate files needed
  # - Clear decision tree
  #
  # TERNARY OPERATOR:
  # condition ? true_value : false_value
  # var.environment == "prod" ? 3 : 1
  # If environment is prod, use 3, otherwise use 1
  #
  # MULTI-CONDITION:
  # Can nest ternaries for more conditions:
  # var.environment == "prod" ? 3 : var.environment == "staging" ? 2 : 1
  # prod → 3, staging → 2, dev → 1
  #
  # Or use map lookup:
  # lookup({dev = 1, staging = 2, prod = 3}, var.environment, 1)
  # Look up environment in map, default to 1 if not found
  #
  # WEB TIER INSTANCE COUNT:
  web_instance_count = var.environment == "prod" ? 3 : var.environment == "staging" ? 2 : 1

  # APP TIER INSTANCE COUNT:
  app_instance_count = var.environment == "prod" ? 3 : var.environment == "staging" ? 2 : 1

  # DATABASE MULTI-AZ:
  # Enable Multi-AZ for production (high availability), disable for dev (cost savings).
  #
  # Multi-AZ RDS:
  # - Enabled: Synchronous replica in different AZ, automatic failover in ~60-120s
  # - Disabled: Single instance, no automatic failover, cheaper (50% cost)
  #
  # COST IMPACT:
  # db.m5.large:
  # - Single-AZ: ~$140/month
  # - Multi-AZ: ~$280/month (2x cost)
  #
  # RECOMMENDATION:
  # - dev: false (cost optimization, acceptable downtime)
  # - staging: true (test Multi-AZ behavior, failover procedures)
  # - prod: true (required for production availability)
  #
  db_multi_az = var.environment == "prod" ? true : false

  # Or more explicitly for multiple environments:
  # db_multi_az = contains(["prod", "staging"], var.environment)
  # True if environment is prod OR staging, false otherwise

  # DATABASE BACKUP RETENTION:
  # Longer retention in production (compliance, disaster recovery),
  # shorter in dev (save storage costs).
  #
  # RDS BACKUP RETENTION:
  # - Minimum: 1 day
  # - Maximum: 35 days
  # - 0 disables automated backups (NOT RECOMMENDED even for dev)
  #
  # STORAGE COST:
  # Backup storage up to database size is free.
  # Beyond that: $0.095/GB-month for most regions.
  #
  # RECOMMENDATIONS:
  # - dev: 1-3 days (can restore from recent backup if needed, but not critical)
  # - staging: 7 days (one week of history for testing restore procedures)
  # - prod: 30 days (compliance often requires 30 days)
  #
  # COMPLIANCE REQUIREMENTS:
  # - HIPAA: 6 years
  # - PCI-DSS: 1 year
  # - SOC 2: Varies (often 90 days minimum)
  # - GDPR: Depends on data retention policy
  #
  # For long-term retention beyond 35 days:
  # - Use RDS snapshots (manual or automatic)
  # - Export to S3 (parquet format for analytics)
  # - AWS Backup service (centralized backup management)
  #
  db_backup_retention_days = var.environment == "prod" ? 30 : var.environment == "staging" ? 7 : 1

  # DELETION PROTECTION:
  # Prevent accidental deletion of critical resources.
  #
  # RDS DELETION PROTECTION:
  # - Enabled: Cannot delete database via API/console (must disable first)
  # - Disabled: Can delete with single command (dangerous!)
  #
  # SCENARIO WITHOUT DELETION PROTECTION:
  # ```bash
  # # Whoops, ran this in prod instead of dev!
  # terraform destroy  # Or aws rds delete-db-instance
  # # Database deleted in seconds, data lost forever (if no backups)
  # ```
  #
  # SCENARIO WITH DELETION PROTECTION:
  # ```bash
  # terraform destroy
  # # Error: Cannot delete database with deletion protection enabled
  # # Must first: aws rds modify-db-instance --no-deletion-protection
  # # Then: terraform destroy
  # # Extra step prevents accidental deletion
  # ```
  #
  # RECOMMENDATION:
  # - dev: false (frequently create/destroy for testing)
  # - staging: true (more stable, but can disable if needed)
  # - prod: true (ALWAYS, no exceptions)
  #
  # DISABLING FOR LEGITIMATE TEARDOWN:
  # If need to delete production database (end of project, migration, etc.):
  # 1. Take final backup manually
  # 2. Disable deletion protection: terraform apply with local.db_deletion_protection = false
  # 3. Delete database: terraform destroy
  # 4. Verify backup is accessible
  #
  db_deletion_protection = var.environment == "prod" ? true : false

  # NAT GATEWAY CONFIGURATION:
  # Single NAT gateway (cheaper) for dev, one per AZ (HA) for prod.
  #
  # This is a more complex example because var.single_nat_gateway is boolean,
  # but we want environment-based logic.
  #
  # OPTION 1: Simple ternary
  # single_nat_gateway = var.environment == "prod" ? false : true
  # - prod: false (multiple NAT gateways)
  # - dev/staging: true (single NAT gateway)
  #
  # OPTION 2: Explicit conditions
  # single_nat_gateway = var.environment == "prod" ? false : var.environment == "staging" ? false : true
  # - prod: false (multiple)
  # - staging: false (multiple, test HA)
  # - dev: true (single, cost optimization)
  #
  # For this example, let's assume:
  # - prod and staging use multiple NAT gateways (HA)
  # - dev uses single NAT gateway (cost)
  #
  single_nat_gateway = var.environment == "dev" ? true : false

  # ALB DELETION PROTECTION:
  # Similar to database deletion protection.
  #
  # Enabled: Cannot delete ALB without first disabling protection.
  # Prevents accidental terraform destroy from taking down production load balancer.
  #
  alb_deletion_protection = var.environment == "prod" ? true : false

  # CLOUDWATCH LOG RETENTION:
  # How long to keep CloudWatch Logs.
  #
  # LOG RETENTION OPTIONS:
  # - 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653 days
  # - 0 = never expire (NOT RECOMMENDED - costs grow indefinitely)
  #
  # COST:
  # - $0.50/GB ingested
  # - $0.03/GB stored per month
  # - Example: 10 GB logs/day for 30 days = $150 ingestion + $9 storage = $159/month
  #
  # RECOMMENDATIONS:
  # - dev: 7 days (short-term debugging, low cost)
  # - staging: 30 days (one month of history for issue investigation)
  # - prod: 90 days (compliance, incident investigation, trend analysis)
  #
  # LONG-TERM LOG STORAGE:
  # For logs beyond retention period, export to S3:
  # - CloudWatch Logs → S3 (automatic export)
  # - S3 Lifecycle Policy → Glacier after 90 days (cheaper long-term storage)
  # - Query old logs with Athena when needed
  #
  # COST COMPARISON (1 year retention):
  # - CloudWatch Logs: $0.03/GB/month × 12 months = $0.36/GB/year
  # - S3 Standard: $0.023/GB/month × 12 months = $0.276/GB/year
  # - S3 Glacier: $0.004/GB/month × 12 months = $0.048/GB/year
  #
  # For long-term retention, export to S3 (cheaper).
  #
  cloudwatch_log_retention_days = var.environment == "prod" ? 90 : var.environment == "staging" ? 30 : 7

  # ELASTICACHE NODE COUNT:
  # Number of cache nodes (Redis cluster nodes).
  #
  # Single node: No replication, no failover, cheapest.
  # Multiple nodes: Replication, automatic failover, higher availability.
  #
  # REDIS CLUSTER SIZES:
  # - 1 node: No replication (if node fails, cache is down)
  # - 2 nodes: 1 primary + 1 replica (automatic failover to replica)
  # - 3+ nodes: 1 primary + multiple replicas (more read capacity)
  #
  # RECOMMENDATION:
  # - dev: 1 (single node, acceptable if cache goes down)
  # - staging: 2 (test failover behavior)
  # - prod: 2-3 (high availability, handle read load)
  #
  elasticache_node_count = var.environment == "prod" ? 2 : 1

  # S3 LIFECYCLE POLICY DAYS:
  # How long to keep objects in S3 before transitioning to cheaper storage or deletion.
  #
  # S3 STORAGE CLASSES:
  # - Standard: $0.023/GB/month (frequent access)
  # - Standard-IA: $0.0125/GB/month (infrequent access, retrieval fee)
  # - Glacier: $0.004/GB/month (archive, minutes to hours retrieval)
  # - Deep Archive: $0.00099/GB/month (long-term archive, 12+ hours retrieval)
  #
  # EXAMPLE LIFECYCLE POLICY:
  # - Day 0-30: S3 Standard (frequently accessed)
  # - Day 30-90: Standard-IA (infrequent access)
  # - Day 90+: Glacier (archive)
  # - Day 365+: Delete (or Deep Archive)
  #
  # COST EXAMPLE (1 TB data):
  # - S3 Standard for 1 year: $23/month × 12 = $276/year
  # - S3 Standard (30 days) + IA (60 days) + Glacier (275 days):
  #   (30/365 × $23) + (60/365 × $12.50) + (275/365 × $4) = $1.89 + $2.05 + $3.01 = $6.95/month × 12 = $83.40/year
  # - Savings: $192.60/year (70% reduction)
  #
  # RECOMMENDATION:
  # - dev: Shorter lifecycle (data less important, save costs)
  # - prod: Longer lifecycle (data important, balance cost and availability)
  #
  s3_lifecycle_transition_days = var.environment == "prod" ? 90 : 30
  s3_lifecycle_expiration_days = var.environment == "prod" ? 365 : 90

  # ENABLE DETAILED MONITORING:
  # EC2 detailed monitoring (1-minute intervals vs 5-minute).
  #
  # BASIC MONITORING (free):
  # - Metrics every 5 minutes
  # - Sufficient for most use cases
  #
  # DETAILED MONITORING ($0.14 per instance per month):
  # - Metrics every 1 minute
  # - Faster detection of issues
  # - Better Auto Scaling responsiveness
  #
  # WHEN TO USE DETAILED MONITORING:
  # - Auto Scaling needs to react quickly (<5 minutes)
  # - Troubleshooting performance issues (need fine-grained data)
  # - Production workloads where 1-minute visibility is worth $0.14/month/instance
  #
  # COST:
  # - 10 instances × $0.14/month = $1.40/month
  # - Usually worth it for production, not for dev
  #
  enable_detailed_monitoring = var.environment == "prod" ? true : false
}

# ADDITIONAL LOCAL VALUES
#
# These could be included if needed:
#
# # CIDR BLOCK CALCULATIONS:
# # Automatically calculate subnet CIDR blocks from VPC CIDR
# locals {
#   # Calculate public subnet CIDRs (first N subnets)
#   public_subnet_cidrs = [
#     for i in range(var.azs_count) :
#     cidrsubnet(var.vpc_cidr, 4, i)  # /16 VPC → /20 subnets
#   ]
#
#   # Calculate private subnet CIDRs (next N subnets)
#   private_subnet_cidrs = [
#     for i in range(var.azs_count) :
#     cidrsubnet(var.vpc_cidr, 4, i + var.azs_count)
#   ]
#
#   # Calculate database subnet CIDRs (next N subnets)
#   database_subnet_cidrs = [
#     for i in range(var.azs_count) :
#     cidrsubnet(var.vpc_cidr, 4, i + 2 * var.azs_count)
#   ]
# }
#
# # CONDITIONAL RESOURCE CREATION:
# # Create certain resources only in specific environments
# locals {
#   create_bastion_host = var.environment == "prod" ? true : false
#   create_read_replica = var.environment == "prod" ? true : false
#   enable_waf          = contains(["prod", "staging"], var.environment)
# }
#
# # RESOURCE NAMING:
# # Pre-compute resource names
# locals {
#   vpc_name               = "${local.name_prefix}-vpc"
#   alb_name               = "${local.name_prefix}-alb"
#   rds_identifier         = "${local.name_prefix}-postgres"
#   elasticache_cluster_id = "${local.name_prefix}-redis"
# }
#
# # SECURITY GROUP RULES:
# # Pre-define security group rule sets
# locals {
#   alb_ingress_rules = [
#     {
#       from_port   = 80
#       to_port     = 80
#       protocol    = "tcp"
#       cidr_blocks = ["0.0.0.0/0"]
#       description = "HTTP from internet"
#     },
#     {
#       from_port   = 443
#       to_port     = 443
#       protocol    = "tcp"
#       cidr_blocks = ["0.0.0.0/0"]
#       description = "HTTPS from internet"
#     }
#   ]
# }

# The locals block can grow as complex as needed, but should remain maintainable.
# Group related values together, add comments explaining non-obvious calculations.
