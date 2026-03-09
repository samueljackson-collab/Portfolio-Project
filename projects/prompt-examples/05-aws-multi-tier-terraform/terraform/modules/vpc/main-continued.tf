# ==============================================================================
# VPC MODULE - NAT GATEWAYS, ROUTE TABLES, AND ADVANCED NETWORKING
# ==============================================================================
# This is a continuation of main.tf showing the remaining VPC resources
# In actual implementation, this would be part of main.tf
# Separated here for clarity in the example
# ==============================================================================

# NAT GATEWAYS (ONE PER AZ)
#
# Provide outbound internet access for private subnets.
# Each NAT Gateway placed in public subnet serves private subnet in same AZ.
#
# MULTI-AZ NAT GATEWAY ARCHITECTURE:
# - NAT Gateway in us-east-1a → Serves private subnet in us-east-1a
# - NAT Gateway in us-east-1b → Serves private subnet in us-east-1b
# - NAT Gateway in us-east-1c → Serves private subnet in us-east-1c
#
# WHY ONE PER AZ:
# - High availability: If one AZ fails, others continue working
# - No cross-AZ traffic: Each private subnet uses local NAT (no cross-AZ fees)
# - Performance: Lower latency (traffic stays in same AZ)
#
# COUNT LOGIC:
# count = var.enable_nat_gateway && !var.single_nat_gateway ? length(var.availability_zones) : 0
# - If NAT enabled AND multi-AZ mode: Create N NAT gateways (one per AZ)
# - Otherwise: 0 (either NAT disabled or using single NAT gateway)
#
# ALLOCATION_ID:
# - References Elastic IP created earlier (aws_eip.nat[count.index].id)
# - Each NAT Gateway gets its own EIP
# - Outbound traffic appears to come from this EIP
#
# SUBNET_ID:
# - NAT Gateway must be in PUBLIC subnet
# - Public subnet has route to Internet Gateway
# - NAT Gateway uses IGW for actual internet access
#
# DEPENDS_ON:
# - Explicit dependency on IGW (even though implicit via subnet)
# - Ensures IGW exists before NAT Gateway creation
# - Prevents rare race condition during creation
#
# HIGH AVAILABILITY:
# - AWS manages NAT Gateway HA within AZ automatically
# - No need for multiple NAT Gateways per AZ
# - If NAT Gateway fails, AWS replaces it automatically
# - Downtime during replacement: ~5-10 minutes
#
# COST (PER NAT GATEWAY):
# - Hourly charge: $0.045/hour = ~$32/month
# - Data processing: $0.045/GB
# - Total for 3 AZs: 3 × $32 = ~$96/month + data processing
#
# COST EXAMPLE (100 GB outbound traffic per month):
# - 3 NAT Gateways: 3 × $32 = $96/month
# - Data processing: 100 GB × $0.045 = $4.50
# - Data transfer (to internet): 100 GB × $0.09 = $9.00
# - Total: $109.50/month
#
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway && !var.single_nat_gateway ? length(var.availability_zones) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-nat-${var.availability_zones[count.index]}"
    }
  )

  # EXPLICIT DEPENDENCY
  # Ensure Internet Gateway exists before creating NAT Gateway
  # NAT Gateway needs IGW to route traffic to internet
  depends_on = [aws_internet_gateway.main]
}

# SINGLE NAT GATEWAY (COST OPTIMIZATION)
#
# Single NAT Gateway serving all private subnets across all AZs.
#
# ARCHITECTURE:
# - One NAT Gateway in public subnet (typically first AZ: us-east-1a)
# - All private subnets route to this single NAT Gateway
# - If NAT's AZ fails, ALL private subnets lose internet access
#
# COST SAVINGS:
# - Single NAT: $32/month
# - Multi-AZ NAT: $96/month (3 AZs)
# - Savings: $64/month (67% reduction)
#
# TRADE-OFF:
# - Save: $64/month
# - Risk: Single point of failure
# - Cross-AZ traffic: Private subnets in AZ-B route to NAT in AZ-A ($0.01/GB)
#
# WHEN TO USE:
# - Development environments
# - Cost-sensitive non-production
# - Low-traffic workloads
# - Acceptable downtime if AZ fails
#
# COUNT LOGIC:
# count = var.enable_nat_gateway && var.single_nat_gateway ? 1 : 0
# - If NAT enabled AND single-NAT mode: Create 1 NAT Gateway
# - Otherwise: 0 (using multi-AZ NAT or NAT disabled)
#
# SUBNET PLACEMENT:
# subnet_id = aws_subnet.public[0].id
# - Place in first public subnet (index 0)
# - Usually us-east-1a (or first AZ in var.availability_zones)
# - Could use different AZ if needed (just change index)
#
resource "aws_nat_gateway" "single" {
  count = var.enable_nat_gateway && var.single_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat_single[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-nat-single"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# PUBLIC ROUTE TABLE
#
# Route table for public subnets.
# All public subnets share one route table (no per-AZ routing needed).
#
# ROUTE TABLE PURPOSE:
# - Defines how traffic is routed within VPC and to internet
# - Each subnet must be associated with exactly one route table
# - Default route table exists automatically, but we create custom ones for control
#
# WHY ONE PUBLIC ROUTE TABLE:
# - All public subnets have identical routing needs:
#   * Local traffic stays in VPC (automatic route)
#   * Internet traffic goes to Internet Gateway
# - No need for per-AZ route tables (same behavior everywhere)
# - Simpler to manage (one table vs three)
#
# DEFAULT ROUTE (0.0.0.0/0):
# - Defined in aws_route resource below
# - Sends all non-VPC traffic to Internet Gateway
# - "Default route" or "default gateway" in networking terms
#
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-public-rt"
      Tier = "public"
    }
  )
}

# PUBLIC SUBNET ROUTE: INTERNET GATEWAY
#
# Default route for public subnets → Internet Gateway.
# All internet-bound traffic goes to IGW.
#
# ROUTE ATTRIBUTES:
# route_table_id: Public route table (created above)
# destination_cidr_block: 0.0.0.0/0 (all IPs, "default route")
# gateway_id: Internet Gateway ID
#
# HOW THIS WORKS:
# 1. Instance in public subnet sends packet to 8.8.8.8 (Google DNS)
# 2. VPC router checks route table for public subnet
# 3. Route table says: "0.0.0.0/0 → IGW"
# 4. 8.8.8.8 matches 0.0.0.0/0 (matches everything)
# 5. Packet sent to Internet Gateway
# 6. IGW NATs private IP → public IP
# 7. Packet reaches internet
#
# ROUTE PRIORITY:
# Most specific route wins:
# - 10.0.0.0/16 (VPC CIDR): Local (automatic, can't delete)
# - 0.0.0.0/0: Internet Gateway (this route)
#
# If packet destination is 10.0.5.10:
# - Matches 10.0.0.0/16 (specific) and 0.0.0.0/0 (general)
# - 10.0.0.0/16 is more specific (/16 vs /0)
# - Packet stays in VPC (local route)
#
# If packet destination is 8.8.8.8:
# - Matches 0.0.0.0/0 only
# - Packet goes to Internet Gateway
#
# WHY SEPARATE RESOURCE:
# Could embed route in route table:
# resource "aws_route_table" "public" {
#   route {
#     cidr_block = "0.0.0.0/0"
#     gateway_id = aws_internet_gateway.main.id
#   }
# }
#
# But separate aws_route resource is better:
# - Clearer intent (explicit route creation)
# - Easier to manage (add/remove routes without recreating table)
# - Better state tracking (route changes don't recreate table)
#
resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id

  # TIMEOUTS
  # Route creation occasionally times out (AWS API delay)
  # Increase timeout for more reliable creation
  timeouts {
    create = "5m"
  }
}

# PUBLIC SUBNET ROUTE TABLE ASSOCIATIONS
#
# Associate each public subnet with the public route table.
# This "activates" the routing rules for those subnets.
#
# ASSOCIATION CONCEPT:
# - Subnets don't inherently know their routes
# - Must associate subnet with route table
# - Association = "Use this route table for this subnet"
#
# COUNT:
# count = length(var.availability_zones)
# - Create one association per public subnet
# - 3 AZs = 3 public subnets = 3 associations
#
# ONE ROUTE TABLE, MULTIPLE ASSOCIATIONS:
# - route_table_id = same for all (aws_route_table.public.id)
# - subnet_id = different for each (aws_subnet.public[count.index].id)
# - Pattern: Many subnets can use same route table
#
# AUTOMATIC ASSOCIATION:
# - If subnet not explicitly associated, uses "main route table"
# - Main route table is VPC's default (usually empty)
# - Best practice: Explicit associations (clear intent)
#
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# PRIVATE ROUTE TABLES (ONE PER AZ)
#
# Separate route table for each private subnet.
# Each routes to local NAT Gateway for high availability.
#
# WHY PER-AZ ROUTE TABLES:
# - Each private subnet needs to route to NAT Gateway in SAME AZ
# - Private subnet in us-east-1a → NAT Gateway in us-east-1a
# - Private subnet in us-east-1b → NAT Gateway in us-east-1b
# - Cannot use single route table (different NAT Gateway per AZ)
#
# COST OPTIMIZATION (SINGLE NAT MODE):
# - If using single NAT Gateway, could use single private route table
# - All private subnets route to same NAT Gateway
# - This code handles both scenarios (multi-NAT and single-NAT)
#
# COUNT:
# count = length(var.availability_zones)
# - Create one route table per AZ
# - 3 AZs = 3 private route tables
#
resource "aws_route_table" "private" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-private-rt-${var.availability_zones[count.index]}"
      Tier = "private"
      AZ   = var.availability_zones[count.index]
    }
  )
}

# PRIVATE SUBNET ROUTE: NAT GATEWAY (MULTI-AZ MODE)
#
# Default route for private subnets → NAT Gateway (multi-AZ mode).
# Each private subnet routes to NAT Gateway in same AZ.
#
# COUNT LOGIC:
# count = var.enable_nat_gateway && !var.single_nat_gateway ? length(var.availability_zones) : 0
# - If multi-AZ NAT mode: Create N routes (one per AZ)
# - Each route uses NAT Gateway in corresponding AZ
#
# NAT GATEWAY MAPPING:
# - Private RT 0 (us-east-1a) → NAT Gateway 0 (us-east-1a)
# - Private RT 1 (us-east-1b) → NAT Gateway 1 (us-east-1b)
# - Private RT 2 (us-east-1c) → NAT Gateway 2 (us-east-1c)
#
# HIGH AVAILABILITY:
# - If NAT in us-east-1a fails, only private subnet in us-east-1a affected
# - Private subnets in us-east-1b and us-east-1c continue working
# - Blast radius: Limited to single AZ
#
# NO CROSS-AZ TRAFFIC:
# - Traffic stays in same AZ (private subnet → NAT Gateway → IGW)
# - Avoids cross-AZ data transfer fees ($0.01/GB)
# - Lower latency (same-AZ communication faster)
#
resource "aws_route" "private_nat_gateway" {
  count = var.enable_nat_gateway && !var.single_nat_gateway ? length(var.availability_zones) : 0

  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main[count.index].id

  timeouts {
    create = "5m"
  }
}

# PRIVATE SUBNET ROUTE: SINGLE NAT GATEWAY (COST OPTIMIZATION MODE)
#
# Default route for private subnets → Single NAT Gateway.
# All private subnets (across all AZs) route to one NAT Gateway.
#
# COUNT LOGIC:
# count = var.enable_nat_gateway && var.single_nat_gateway ? length(var.availability_zones) : 0
# - If single-NAT mode: Create N routes (one per private route table)
# - All routes point to same NAT Gateway
#
# NAT GATEWAY MAPPING:
# - Private RT 0 (us-east-1a) → Single NAT Gateway
# - Private RT 1 (us-east-1b) → Single NAT Gateway (same one)
# - Private RT 2 (us-east-1c) → Single NAT Gateway (same one)
#
# CROSS-AZ TRAFFIC:
# - Private subnet in us-east-1b sends traffic to NAT in us-east-1a
# - Crosses AZ boundary (incurs cross-AZ fee: $0.01/GB)
# - Example: 100 GB from us-east-1b to internet via NAT in us-east-1a
#   * NAT processing: 100 GB × $0.045 = $4.50
#   * Cross-AZ transfer: 100 GB × $0.01 = $1.00
#   * Internet transfer: 100 GB × $0.09 = $9.00
#   * Total: $14.50
#
# SINGLE POINT OF FAILURE:
# - If single NAT Gateway fails (or its AZ fails), all private subnets lose internet
# - Manual intervention required (create new NAT Gateway in different AZ)
# - Downtime: ~10-30 minutes (create NAT, update routes, propagate)
#
resource "aws_route" "private_nat_gateway_single" {
  count = var.enable_nat_gateway && var.single_nat_gateway ? length(var.availability_zones) : 0

  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.single[0].id

  timeouts {
    create = "5m"
  }
}

# PRIVATE SUBNET ROUTE TABLE ASSOCIATIONS
#
# Associate each private subnet with its corresponding route table.
#
# MAPPING:
# - Private subnet 0 (us-east-1a) → Private route table 0
# - Private subnet 1 (us-east-1b) → Private route table 1
# - Private subnet 2 (us-east-1c) → Private route table 2
#
resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# DATABASE ROUTE TABLE
#
# Route table for database subnets.
# NO internet access (no NAT Gateway routes, no IGW routes).
#
# ISOLATION:
# - Only VPC-local routes (automatic)
# - No 0.0.0.0/0 route (no internet)
# - Database subnets cannot reach internet
# - Internet cannot reach database subnets (double isolation)
#
# WHY NO INTERNET:
# - Security: Databases shouldn't need internet access
# - Compliance: Many frameworks require database isolation
# - Attack surface: Even if database compromised, can't call home
#
# AWS SERVICE ACCESS:
# - If database needs S3 (backups), ElastiCache (migration), etc.
# - Use VPC Endpoints (private connection to AWS services)
# - No internet required
# - See aws_vpc_endpoint resources below
#
# ONE TABLE FOR ALL DATABASE SUBNETS:
# - All database subnets have identical routing (none!)
# - No need for per-AZ tables
#
resource "aws_route_table" "database" {
  count = var.create_database_subnets ? 1 : 0

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-database-rt"
      Tier = "database"
    }
  )
}

# DATABASE SUBNET ROUTE TABLE ASSOCIATIONS
#
# Associate each database subnet with database route table.
#
# COUNT LOGIC:
# count = var.create_database_subnets ? length(var.availability_zones) : 0
# - If database subnets enabled: Create associations
# - If database subnets disabled: 0 associations
#
resource "aws_route_table_association" "database" {
  count = var.create_database_subnets ? length(var.availability_zones) : 0

  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database[0].id
}

# VPC FLOW LOGS
#
# Capture network traffic metadata for security and troubleshooting.
# Logs all ACCEPT and REJECT traffic at network interface level.
#
# WHAT ARE FLOW LOGS:
# - Capture metadata about IP traffic: source IP, dest IP, ports, protocol, action
# - NOT full packet capture (too expensive, privacy concerns)
# - Logged to CloudWatch Logs or S3
#
# FLOW LOG RECORD EXAMPLE:
# 2 123456789012 eni-abc123 10.0.1.5 203.0.113.10 49152 443 6 10 840 1620000000 1620000300 ACCEPT OK
#
# Fields:
# - version: 2
# - account-id: 123456789012
# - interface-id: eni-abc123
# - srcaddr: 10.0.1.5 (private instance IP)
# - dstaddr: 203.0.113.10 (external IP)
# - srcport: 49152 (ephemeral port)
# - dstport: 443 (HTTPS)
# - protocol: 6 (TCP)
# - packets: 10
# - bytes: 840
# - start: 1620000000 (Unix timestamp)
# - end: 1620000300
# - action: ACCEPT (or REJECT)
# - log-status: OK
#
# USE CASES:
#
# 1. SECURITY:
#    - Detect unusual traffic patterns (port scanning, DDoS)
#    - Identify compromised instances (unexpected outbound connections)
#    - Investigate security incidents (who accessed what, when)
#    - Compliance: Many frameworks require network logging
#
# 2. TROUBLESHOOTING:
#    - Debug connectivity issues (is traffic reaching instance?)
#    - Identify blocked traffic (security group rejections)
#    - Find bandwidth hogs (which instance uses most data)
#
# 3. COST OPTIMIZATION:
#    - Identify chatty instances (optimize to reduce data transfer)
#    - Find cross-AZ traffic (can you optimize to same-AZ?)
#    - Detect misconfigured applications (polling too frequently)
#
# TRAFFIC TYPE:
# - ACCEPT: Traffic allowed by security groups
# - REJECT: Traffic blocked by security groups or NACLs
# - ALL: Both accepts and rejects (recommended for full visibility)
#
# DESTINATION:
# - CloudWatch Logs: Real-time querying, retention management, alarms
# - S3: Long-term storage, cheaper, query with Athena
#
# COST:
# - Data ingestion: $0.50 per GB
# - CloudWatch storage: $0.03 per GB per month
# - S3 storage: $0.023 per GB per month (Standard)
# - Typical VPC: 1-5 GB flow logs per day
# - Monthly cost: ~$15-75 ingestion + storage
#
# EXAMPLE COST (2 GB flow logs per day):
# - Ingestion: 60 GB/month × $0.50 = $30
# - Storage (CloudWatch, 90 day retention): 60 GB × $0.03 = $1.80
# - Total: ~$32/month
#
# FIELDS TO LOG:
# Default fields include basic info (IPs, ports, action).
# Custom format can include additional fields:
# - vpc-id, subnet-id, instance-id
# - tcp-flags, pkt-srcaddr, pkt-dstaddr
# - More cost (more data logged)
#
# CONDITIONAL CREATION:
# count = var.enable_flow_logs ? 1 : 0
# - Enable in production (security, compliance)
# - Disable in dev (save ~$30/month)
#
resource "aws_flow_log" "main" {
  count = var.enable_flow_logs ? 1 : 0

  # LOG DESTINATION
  # cloudwatch-logs or s3
  # CloudWatch: Real-time, queryable, alertable
  # S3: Cheaper, long-term, query with Athena
  log_destination_type = var.flow_log_destination_type
  log_destination      = var.flow_log_destination_type == "cloud-watch-logs" ? aws_cloudwatch_log_group.flow_log[0].arn : var.flow_log_s3_bucket_arn

  # IAM ROLE (CloudWatch Logs only)
  # Flow Logs needs permission to write to CloudWatch
  # S3 doesn't need IAM role (uses bucket policy)
  iam_role_arn = var.flow_log_destination_type == "cloud-watch-logs" ? aws_iam_role.flow_log[0].arn : null

  # VPC TO MONITOR
  vpc_id = aws_vpc.main.id

  # TRAFFIC TYPE
  # ACCEPT: Only accepted traffic (saves cost, less visibility)
  # REJECT: Only rejected traffic (identify blocked traffic)
  # ALL: Both accepted and rejected (recommended for full visibility)
  traffic_type = var.flow_log_traffic_type

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-flow-log"
    }
  )
}

# CloudWatch Log Group (if using CloudWatch Logs destination)
resource "aws_cloudwatch_log_group" "flow_log" {
  count = var.enable_flow_logs && var.flow_log_destination_type == "cloud-watch-logs" ? 1 : 0

  name              = "/aws/vpc/flow-logs/${var.name_prefix}"
  retention_in_days = var.flow_log_retention_days

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-flow-log-group"
    }
  )
}

# IAM Role for Flow Logs (CloudWatch Logs only)
resource "aws_iam_role" "flow_log" {
  count = var.enable_flow_logs && var.flow_log_destination_type == "cloud-watch-logs" ? 1 : 0

  name = "${var.name_prefix}-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for Flow Logs
resource "aws_iam_role_policy" "flow_log" {
  count = var.enable_flow_logs && var.flow_log_destination_type == "cloud-watch-logs" ? 1 : 0

  name = "${var.name_prefix}-flow-log-policy"
  role = aws_iam_role.flow_log[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

# VPC module continues with VPC Endpoints, Network ACLs, and other advanced features
# This demonstrates the exhaustive documentation pattern
# Complete file would be 3,000-4,000+ lines with all VPC networking resources
