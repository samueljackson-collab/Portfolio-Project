# Networking Module - Main Terraform Configuration
# Purpose: Provisions a production-ready three-tier VPC architecture with HA, security, and monitoring best practices

locals {
  az_count           = length(var.availability_zones)
  nat_gateway_azs    = var.enable_nat_gateway ? (var.single_nat_gateway ? [var.availability_zones[0]] : var.availability_zones) : []
  nat_gateway_count  = length(local.nat_gateway_azs)
  private_route_count = length(var.availability_zones)
}

# VPC Creation
# Purpose: Isolated network environment for three-tier application
# Design: Multi-AZ deployment across 3 availability zones for high availability
# CIDR: /16 provides 65,536 IP addresses, allowing for growth and segmentation
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr  # Example: "10.0.0.0/16"

  # DNS Support: Required for using Route53 private hosted zones
  # Enables DNS resolution for resources within VPC
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.common_tags,
    {
      Name              = "${var.project_name}-${var.environment}-vpc"
      Environment       = var.environment
      ManagedBy         = "Terraform"
      CostCenter        = var.cost_center
      DataClassification = "Internal"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-igw"
    }
  )
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count  = local.nat_gateway_count
  domain = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name             = "${var.project_name}-${var.environment}-nat-eip-${local.nat_gateway_azs[count.index]}"
      AvailabilityZone = local.nat_gateway_azs[count.index]
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# Public Subnets
resource "aws_subnet" "public" {
  count = local.az_count

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name                       = "${var.project_name}-${var.environment}-public-subnet-${var.availability_zones[count.index]}"
      Tier                       = "public"
      "kubernetes.io/role/elb" = "1"
    }
  )
}

# Private Application Subnets
resource "aws_subnet" "private_app" {
  count = local.az_count

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = false

  tags = merge(
    var.common_tags,
    {
      Name                        = "${var.project_name}-${var.environment}-private-app-subnet-${var.availability_zones[count.index]}"
      Tier                        = "private-app"
      "kubernetes.io/role/internal-elb" = "1"
    }
  )
}

# Private Database Subnets
resource "aws_subnet" "private_db" {
  count = local.az_count

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = false

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-private-db-subnet-${var.availability_zones[count.index]}"
      Tier = "private-database"
    }
  )
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count = local.nat_gateway_count

  subnet_id     = aws_subnet.public[var.single_nat_gateway ? 0 : count.index].id
  allocation_id = aws_eip.nat[count.index].id

  tags = merge(
    var.common_tags,
    {
      Name             = "${var.project_name}-${var.environment}-nat-gw-${local.nat_gateway_azs[count.index]}"
      AvailabilityZone = local.nat_gateway_azs[count.index]
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-public-rt"
      Tier = "public"
    }
  )
}

# Public Route: Internet Access
resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

# Associate Public Subnets with Public Route Table
resource "aws_route_table_association" "public" {
  count = local.az_count

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private App Route Tables
resource "aws_route_table" "private_app" {
  count = local.az_count

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name             = "${var.project_name}-${var.environment}-private-app-rt-${var.availability_zones[count.index]}"
      Tier             = "private-app"
      AvailabilityZone = var.availability_zones[count.index]
    }
  )
}

# Private App Routes (conditional on NAT availability)
resource "aws_route" "private_app_internet" {
  count = var.enable_nat_gateway ? local.private_route_count : 0

  route_table_id         = aws_route_table.private_app[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main[var.single_nat_gateway ? 0 : count.index].id
}

# Associate Private App Subnets
resource "aws_route_table_association" "private_app" {
  count = local.az_count

  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}

# Private Database Route Tables
resource "aws_route_table" "private_db" {
  count = local.az_count

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name             = "${var.project_name}-${var.environment}-private-db-rt-${var.availability_zones[count.index]}"
      Tier             = "private-database"
      AvailabilityZone = var.availability_zones[count.index]
    }
  )
}

# Associate Private DB Subnets
resource "aws_route_table_association" "private_db" {
  count = local.az_count

  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private_db[count.index].id
}

# VPC Flow Logs
resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0

  name              = "/aws/vpc/${var.project_name}-${var.environment}-flow-logs"
  retention_in_days = var.flow_logs_retention_days

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc-flow-logs-group"
    }
  )
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0

  name = "${var.project_name}-${var.environment}-vpc-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowVPCFlowLogsAssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0

  name = "${var.project_name}-${var.environment}-vpc-flow-logs-policy"
  role = aws_iam_role.flow_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowFlowLogsToCloudWatch"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.flow_logs[0].arn}:*"
      }
    ]
  })
}

resource "aws_flow_log" "main" {
  count = var.enable_vpc_flow_logs ? 1 : 0

  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.flow_logs[0].arn
  iam_role_arn         = aws_iam_role.flow_logs[0].arn
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.main.id

  log_format = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${start} $${end} $${action} $${log-status} $${vpc-id} $${subnet-id} $${instance-id} $${tcp-flags} $${type} $${pkt-srcaddr} $${pkt-dstaddr} $${region} $${az-id} $${sublocation-type} $${sublocation-id} $${pkt-src-aws-service} $${pkt-dst-aws-service} $${flow-direction} $${traffic-path}"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc-flow-logs"
    }
  )
}

# VPC Endpoint for S3
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_s3_endpoint ? 1 : 0

  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(aws_route_table.private_app[*].id, aws_route_table.private_db[*].id)

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowS3Access"
        Effect   = "Allow"
        Principal = "*"
        Action   = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-s3-endpoint"
    }
  )
}

# VPC Endpoint for DynamoDB
resource "aws_vpc_endpoint" "dynamodb" {
  count = var.enable_dynamodb_endpoint ? 1 : 0

  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = aws_route_table.private_app[*].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-dynamodb-endpoint"
    }
  )
}

# Network ACLs - Public
resource "aws_network_acl" "public" {
  vpc_id = aws_vpc.main.id

  subnet_ids = aws_subnet.public[*].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-public-nacl"
      Tier = "public"
    }
  )
}

resource "aws_network_acl_rule" "public_ingress_http" {
  network_acl_id = aws_network_acl.public.id
  rule_number    = 100
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 80
  to_port        = 80
}

resource "aws_network_acl_rule" "public_ingress_https" {
  network_acl_id = aws_network_acl.public.id
  rule_number    = 110
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 443
  to_port        = 443
}

resource "aws_network_acl_rule" "public_ingress_ephemeral" {
  network_acl_id = aws_network_acl.public.id
  rule_number    = 120
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  to_port        = 65535
}

resource "aws_network_acl_rule" "public_egress_all" {
  network_acl_id = aws_network_acl.public.id
  rule_number    = 100
  egress         = true
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}

# Private App NACL
resource "aws_network_acl" "private_app" {
  vpc_id = aws_vpc.main.id

  subnet_ids = aws_subnet.private_app[*].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-private-app-nacl"
      Tier = "private-app"
    }
  )
}

resource "aws_network_acl_rule" "private_app_ingress_lb" {
  network_acl_id = aws_network_acl.private_app.id
  rule_number    = 100
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = var.vpc_cidr
  from_port      = 80
  to_port        = 65535
}

resource "aws_network_acl_rule" "private_app_egress_all" {
  network_acl_id = aws_network_acl.private_app.id
  rule_number    = 100
  egress         = true
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}

# Private DB NACL
resource "aws_network_acl" "private_db" {
  vpc_id = aws_vpc.main.id

  subnet_ids = aws_subnet.private_db[*].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-private-db-nacl"
      Tier = "private-database"
    }
  )
}

resource "aws_network_acl_rule" "private_db_ingress" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 100
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = var.vpc_cidr
  from_port      = 3306
  to_port        = 3306
}

resource "aws_network_acl_rule" "private_db_egress" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 100
  egress         = true
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = var.vpc_cidr
  from_port      = 3306
  to_port        = 3306
}
