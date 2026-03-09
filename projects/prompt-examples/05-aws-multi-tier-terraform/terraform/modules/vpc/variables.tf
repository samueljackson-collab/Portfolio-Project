# ==============================================================================
# VPC MODULE - INPUT VARIABLES
# ==============================================================================
#
# PURPOSE:
# Define all input variables for the VPC module.
# These variables allow customization of VPC configuration per environment.
#
# VARIABLE ORGANIZATION:
# 1. Naming and Tagging
# 2. Network Configuration (CIDR, AZs)
# 3. Subnet Configuration
# 4. NAT Gateway Configuration
# 5. VPC Flow Logs Configuration
# 6. VPC Endpoints Configuration (optional)
# 7. Feature Flags
#
# ==============================================================================

# ------------------------------------------------------------------------------
# NAMING AND TAGGING
# ------------------------------------------------------------------------------

variable "name_prefix" {
  description = <<-EOT
    Name prefix for all VPC resources.

    Used to construct resource names: {name_prefix}-{resource_type}
    Example: "myapp-prod" becomes "myapp-prod-vpc", "myapp-prod-igw", etc.

    REQUIREMENTS:
    - Lowercase alphanumeric and hyphens only
    - Maximum 32 characters
    - Must start with a letter

    NAMING PATTERN:
    Typically: {project}-{environment}
    - myapp-dev
    - myapp-staging
    - myapp-prod
  EOT
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,31}$", var.name_prefix))
    error_message = "Name prefix must start with letter, contain only lowercase letters, numbers, hyphens, and be 1-32 characters."
  }
}

variable "tags" {
  description = <<-EOT
    Common tags to apply to all VPC resources.

    Merged with resource-specific tags for each resource.

    RECOMMENDED TAGS:
    - Environment: dev, staging, prod
    - Project: Application or project name
    - ManagedBy: terraform
    - Owner: Team or individual
    - CostCenter: Finance cost center

    USAGE:
    tags = {
      Environment = "prod"
      Project     = "myapp"
      ManagedBy   = "terraform"
    }
  EOT
  type        = map(string)
  default     = {}
}

# ------------------------------------------------------------------------------
# NETWORK CONFIGURATION
# ------------------------------------------------------------------------------

variable "vpc_cidr" {
  description = <<-EOT
    CIDR block for the VPC.

    Defines the total IP address space for the VPC.

    RECOMMENDED SIZES:
    - /16 (65,536 IPs): Standard for most deployments
    - /20 (4,096 IPs): Small deployments
    - /24 (256 IPs): Very small, testing only

    CIDR RANGE SELECTION:
    Use RFC 1918 private ranges:
    - 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
    - 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
    - 192.168.0.0/16 (192.168.0.0 - 192.168.255.255)

    AVOID CONFLICTS:
    - Don't use 192.168.0.0/16 (common in home networks)
    - Don't use 172.17.0.0/16 (Docker default)
    - Don't overlap with on-premises networks
    - Don't overlap with other VPCs (if peering)

    RECOMMENDED PATTERN:
    Use 10.x.0.0/16 where x is unique per environment:
    - 10.0.0.0/16 (dev)
    - 10.1.0.0/16 (staging)
    - 10.2.0.0/16 (prod)

    EXAMPLE:
    vpc_cidr = "10.0.0.0/16"
  EOT
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }

  validation {
    condition     = tonumber(split("/", var.vpc_cidr)[1]) <= 28
    error_message = "VPC CIDR prefix must be /28 or larger (smaller number = more IPs)."
  }
}

variable "availability_zones" {
  description = <<-EOT
    List of availability zones for subnet creation.

    MULTI-AZ ARCHITECTURE:
    Subnets are created in each specified AZ for high availability.

    RECOMMENDATIONS:
    - Minimum 2 AZs for production (HA requirement)
    - Recommended 3 AZs (AWS best practice)
    - Maximum 6 AZs (diminishing returns)

    COST IMPLICATIONS:
    More AZs = higher costs:
    - NAT Gateway: ~$32/month per AZ
    - Cross-AZ data transfer: $0.01/GB

    EXAMPLE:
    availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

    OR dynamically from data source:
    availability_zones = data.aws_availability_zones.available.names
  EOT
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) >= 2 && length(var.availability_zones) <= 6
    error_message = "Must specify between 2 and 6 availability zones."
  }
}

# ------------------------------------------------------------------------------
# SUBNET CONFIGURATION
# ------------------------------------------------------------------------------

variable "create_database_subnets" {
  description = <<-EOT
    Whether to create dedicated database subnets.

    DATABASE SUBNET BENEFITS:
    - Security isolation (separate from application tier)
    - No internet access (databases shouldn't need internet)
    - Compliance requirement for many frameworks
    - Network performance (dedicated bandwidth)

    WHEN TO ENABLE:
    - Using RDS, ElastiCache, Redshift, or other managed databases
    - Compliance requirements (PCI-DSS, HIPAA)
    - Production environments

    WHEN TO DISABLE:
    - No managed databases in this VPC
    - Databases deployed elsewhere
    - Cost optimization for dev environments

    DEFAULT: true (best practice)
  EOT
  type        = bool
  default     = true
}

variable "enable_kubernetes_tags" {
  description = <<-EOT
    Add Kubernetes/EKS discovery tags to subnets.

    EKS SUBNET DISCOVERY:
    EKS automatically discovers subnets for load balancers using tags:
    - Public subnets: kubernetes.io/role/elb = "1"
    - Private subnets: kubernetes.io/role/internal-elb = "1"

    WHEN TO ENABLE:
    - Deploying Amazon EKS in this VPC
    - Using Kubernetes with AWS Load Balancer Controller

    WHEN TO DISABLE:
    - Not using EKS or Kubernetes
    - Managing load balancers manually

    DEFAULT: false (not all VPCs use Kubernetes)
  EOT
  type        = bool
  default     = false
}

# ------------------------------------------------------------------------------
# NAT GATEWAY CONFIGURATION
# ------------------------------------------------------------------------------

variable "enable_nat_gateway" {
  description = <<-EOT
    Enable NAT Gateways for private subnet internet access.

    WHAT NAT GATEWAYS DO:
    Provide outbound internet access for resources in private subnets
    while preventing inbound connections from the internet.

    WHEN YOU NEED NAT GATEWAYS:
    - Private instances need to download updates (yum, apt, pip, npm)
    - Applications call external APIs (Stripe, Twilio, AWS services)
    - Lambda functions in VPC need internet access
    - ECS tasks pull Docker images from Docker Hub

    WHEN YOU DON'T NEED NAT GATEWAYS:
    - All resources in public subnets (not recommended)
    - Using VPC endpoints for all AWS services
    - Completely air-gapped environment

    COST:
    - Per NAT Gateway: ~$32/month
    - Data processing: $0.045/GB
    - 3 AZs: ~$96/month + data processing

    ALTERNATIVES:
    - VPC Endpoints: Free for S3/DynamoDB, $0.01/GB for others
    - NAT Instance: Cheaper but requires management
    - No internet: Isolate completely

    DEFAULT: true (most applications need internet)
  EOT
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = <<-EOT
    Use single NAT Gateway instead of one per AZ (cost optimization).

    ARCHITECTURE COMPARISON:

    Multi-AZ NAT (single_nat_gateway = false):
    - NAT Gateway in each AZ (3 AZs = 3 NAT Gateways)
    - Cost: ~$96/month (3 × $32)
    - High availability: AZ failure doesn't affect other AZs
    - No cross-AZ traffic (traffic stays local)
    - Recommended for: Production

    Single NAT (single_nat_gateway = true):
    - One NAT Gateway in one AZ
    - Cost: ~$32/month
    - Single point of failure: NAT's AZ failure = all private subnets lose internet
    - Cross-AZ traffic: $0.01/GB for traffic from other AZs
    - Recommended for: Development, cost-sensitive non-production

    FAILURE SCENARIO:

    Multi-AZ NAT:
    - AZ-1 fails → Only AZ-1 private subnet loses internet
    - AZ-2 and AZ-3 continue working normally
    - Applications remain available (reduced capacity)

    Single NAT:
    - NAT's AZ fails → ALL private subnets lose internet
    - Applications cannot download updates, call APIs
    - Requires manual intervention (create new NAT in different AZ)

    MONTHLY COST EXAMPLE (3 AZs, 100 GB outbound):

    Multi-AZ NAT:
    - 3 NAT Gateways: $96
    - Data processing: 100 GB × $0.045 = $4.50
    - Cross-AZ transfer: $0
    - Total: $100.50

    Single NAT:
    - 1 NAT Gateway: $32
    - Data processing: 100 GB × $0.045 = $4.50
    - Cross-AZ transfer: ~$1 (estimated)
    - Total: $37.50
    - Savings: $63/month (63%)

    RECOMMENDATION:
    - dev: true (optimize cost)
    - staging: false (test HA behavior)
    - prod: false (maximize availability)

    DEFAULT: false (high availability by default)
  EOT
  type        = bool
  default     = false
}

# ------------------------------------------------------------------------------
# VPC FLOW LOGS CONFIGURATION
# ------------------------------------------------------------------------------

variable "enable_flow_logs" {
  description = <<-EOT
    Enable VPC Flow Logs for network traffic monitoring.

    WHAT ARE FLOW LOGS:
    Capture metadata about network traffic (IPs, ports, protocols, accept/reject).
    NOT full packet capture (too expensive, privacy concerns).

    USE CASES:

    1. SECURITY:
       - Detect unusual traffic patterns (port scanning, DDoS)
       - Identify compromised instances
       - Investigate security incidents
       - Compliance requirement

    2. TROUBLESHOOTING:
       - Debug connectivity issues
       - Identify blocked traffic
       - Find bandwidth hogs

    3. COST OPTIMIZATION:
       - Identify chatty instances
       - Find cross-AZ traffic
       - Detect misconfigurations

    COST (2 GB logs per day):
    - Data ingestion: 60 GB/month × $0.50 = $30
    - Storage (90 days): 60 GB × $0.03 = $1.80
    - Total: ~$32/month

    RECOMMENDATION:
    - dev: false (save $32/month)
    - staging: true (test monitoring)
    - prod: true (security, compliance)

    DEFAULT: false (optional feature, has cost)
  EOT
  type        = bool
  default     = false
}

variable "flow_log_destination_type" {
  description = <<-EOT
    Destination for VPC Flow Logs: cloud-watch-logs or s3.

    CLOUD-WATCH-LOGS:
    - Real-time querying with CloudWatch Insights
    - Set up alarms based on log data
    - Retention management (1 day to never expire)
    - Cost: $0.50/GB ingestion + $0.03/GB/month storage
    - Use when: Need real-time monitoring and alerting

    S3:
    - Long-term storage (cheaper)
    - Query with Amazon Athena
    - Lifecycle policies (transition to Glacier)
    - Cost: $0.50/GB ingestion + $0.023/GB/month storage
    - Use when: Long-term retention, cost optimization

    COST COMPARISON (60 GB/month, 90-day retention):
    - CloudWatch: $30 ingestion + $1.80 storage = $31.80
    - S3: $30 ingestion + $1.38 storage = $31.38
    - Savings: Minimal for short retention

    LONG-TERM (1 year retention):
    - CloudWatch: $30 ingestion + $21.60 storage = $51.60/month
    - S3 Standard: $30 ingestion + $16.56 storage = $46.56/month
    - S3 Glacier: $30 ingestion + $2.88 storage = $32.88/month

    RECOMMENDATION:
    - Real-time monitoring: cloud-watch-logs
    - Long-term retention: s3

    DEFAULT: "cloud-watch-logs" (most flexible)
  EOT
  type        = string
  default     = "cloud-watch-logs"

  validation {
    condition     = contains(["cloud-watch-logs", "s3"], var.flow_log_destination_type)
    error_message = "Flow log destination must be 'cloud-watch-logs' or 's3'."
  }
}

variable "flow_log_s3_bucket_arn" {
  description = <<-EOT
    S3 bucket ARN for flow logs (required if flow_log_destination_type = "s3").

    BUCKET REQUIREMENTS:
    - Must have bucket policy allowing VPC Flow Logs to write
    - Recommended: Enable versioning and encryption
    - Lifecycle policy: Transition to Glacier after 90 days

    EXAMPLE BUCKET POLICY:
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "AWSLogDeliveryWrite",
          "Effect": "Allow",
          "Principal": {
            "Service": "delivery.logs.amazonaws.com"
          },
          "Action": "s3:PutObject",
          "Resource": "arn:aws:s3:::my-flow-logs-bucket/*"
        }
      ]
    }

    EXAMPLE:
    flow_log_s3_bucket_arn = "arn:aws:s3:::my-flow-logs-bucket"
  EOT
  type        = string
  default     = null
}

variable "flow_log_traffic_type" {
  description = <<-EOT
    Type of traffic to log: ACCEPT, REJECT, or ALL.

    ACCEPT:
    - Only log traffic allowed by security groups
    - Use case: Monitor accepted traffic patterns
    - Cost: Lower (less data)

    REJECT:
    - Only log traffic blocked by security groups/NACLs
    - Use case: Identify attack attempts, misconfigurations
    - Cost: Lower (less data)

    ALL:
    - Log both accepted and rejected traffic
    - Use case: Complete visibility, security analysis, compliance
    - Cost: Higher (more data)

    RECOMMENDATION:
    - ALL for production (full visibility)
    - REJECT for security-focused monitoring
    - ACCEPT for traffic analysis

    DEFAULT: "ALL" (complete visibility)
  EOT
  type        = string
  default     = "ALL"

  validation {
    condition     = contains(["ACCEPT", "REJECT", "ALL"], var.flow_log_traffic_type)
    error_message = "Traffic type must be ACCEPT, REJECT, or ALL."
  }
}

variable "flow_log_retention_days" {
  description = <<-EOT
    CloudWatch Logs retention in days (only applies if using cloud-watch-logs).

    VALID VALUES:
    1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653

    COST IMPACT (60 GB logs per month):
    - 7 days: 60 GB × $0.03 = $1.80/month
    - 30 days: 60 GB × $0.03 = $1.80/month (same, cost is per GB stored)
    - 90 days: 60 GB × $0.03 = $1.80/month (still same)

    Wait, CloudWatch storage is cumulative:
    - 7 days: 14 GB total × $0.03 = $0.42/month
    - 30 days: 60 GB total × $0.03 = $1.80/month
    - 90 days: 180 GB total × $0.03 = $5.40/month

    RECOMMENDATION:
    - dev: 7 days
    - staging: 30 days
    - prod: 90 days (compliance, incident investigation)

    LONG-TERM STORAGE:
    Export to S3 with lifecycle policies for retention > 90 days.

    DEFAULT: 7 (short retention for cost control)
  EOT
  type        = number
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.flow_log_retention_days)
    error_message = "Retention must be a valid CloudWatch Logs retention period."
  }
}

# ------------------------------------------------------------------------------
# VPC ENDPOINTS CONFIGURATION (OPTIONAL)
# ------------------------------------------------------------------------------

variable "enable_s3_endpoint" {
  description = <<-EOT
    Create VPC endpoint for S3 (Gateway endpoint, free).

    BENEFITS:
    - Private connection to S3 (traffic doesn't leave AWS network)
    - No NAT Gateway data processing fees for S3 traffic
    - Better performance (lower latency)
    - Enhanced security (traffic doesn't traverse internet)

    COST SAVINGS EXAMPLE:
    If private instances transfer 500 GB/month to S3:

    Without S3 endpoint:
    - NAT Gateway processing: 500 GB × $0.045 = $22.50/month

    With S3 endpoint:
    - NAT Gateway processing: $0 (bypasses NAT)
    - S3 endpoint: $0 (gateway endpoints are free)
    - Savings: $22.50/month

    GATEWAY ENDPOINT:
    - Free (no hourly charges, no data processing fees)
    - Works with S3 and DynamoDB only
    - Added to route tables automatically

    RECOMMENDATION:
    - Always enable (free, only benefits)

    DEFAULT: true
  EOT
  type        = bool
  default     = true
}

variable "enable_dynamodb_endpoint" {
  description = <<-EOT
    Create VPC endpoint for DynamoDB (Gateway endpoint, free).

    Same benefits as S3 endpoint:
    - Free gateway endpoint
    - No NAT Gateway fees for DynamoDB traffic
    - Better performance and security

    RECOMMENDATION:
    - Enable if using DynamoDB
    - No cost to enable even if not used

    DEFAULT: false (not all applications use DynamoDB)
  EOT
  type        = bool
  default     = false
}

# ------------------------------------------------------------------------------
# ADVANCED CONFIGURATION (OPTIONAL)
# ------------------------------------------------------------------------------

variable "enable_dns_hostnames" {
  description = <<-EOT
    Enable DNS hostnames for instances with public IPs.

    WHEN ENABLED:
    Instances with public IPs get DNS names:
    ec2-54-123-45-67.compute-1.amazonaws.com

    REQUIRED FOR:
    - RDS endpoints
    - ElastiCache endpoints
    - ELB DNS names
    - Route53 private hosted zones

    RECOMMENDATION:
    - Always true (no cost, only benefits)

    DEFAULT: true
  EOT
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = <<-EOT
    Enable DNS resolution via AWS DNS server (VPC CIDR + 2).

    REQUIRED FOR:
    - VPC endpoints
    - Route53 private hosted zones
    - RDS/ElastiCache DNS names

    RECOMMENDATION:
    - Always true (required for most use cases)

    DEFAULT: true
  EOT
  type        = bool
  default     = true
}

variable "instance_tenancy" {
  description = <<-EOT
    Default instance tenancy: default or dedicated.

    DEFAULT:
    - Instances run on shared hardware
    - Standard pricing
    - Can override per-instance

    DEDICATED:
    - Instances run on hardware dedicated to your account
    - ~10% more expensive
    - Required for some compliance (HIPAA, PCI-DSS level 1)

    RECOMMENDATION:
    - Use "default" (cheaper, override per-instance if needed)
    - Use "dedicated" only if compliance requires

    DEFAULT: "default"
  EOT
  type        = string
  default     = "default"

  validation {
    condition     = contains(["default", "dedicated"], var.instance_tenancy)
    error_message = "Instance tenancy must be 'default' or 'dedicated'."
  }
}

# Complete variables.tf with all VPC configuration options
# This demonstrates the exhaustive documentation pattern for module variables
