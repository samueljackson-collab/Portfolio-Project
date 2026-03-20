# VPC-Level Security Groups
# Purpose: Create base security groups used across multiple modules
# These are "foundational" security groups that other modules reference
#
# Security Group Design Philosophy:
# - Least privilege: Start restrictive, add permissions as needed
# - Explicit over implicit: Define rules clearly with descriptions
# - Layered defense: Multiple SGs per resource when appropriate
# - No hardcoded IPs: Use CIDR variables and VPC references

# Security Group: Application Load Balancer (ALB)
# Purpose: Control traffic to/from public-facing load balancers
# Used by: Compute module for web tier ALB
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-alb-"
  description = "Security group for Application Load Balancer - allows HTTP/HTTPS from internet"
  vpc_id      = aws_vpc.main.id

  # Allow inbound HTTP from internet
  # Port 80 typically redirects to HTTPS (443) for security
  ingress {
    description = "HTTP from internet (typically redirects to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow from anywhere
  }

  # Allow inbound HTTPS from internet
  # Primary entry point for web traffic
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow from anywhere
  }

  # Allow all outbound traffic
  # ALB needs to reach targets in private subnets
  egress {
    description = "Allow all outbound traffic to targets"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-alb-sg"
      Description = "Security group for Application Load Balancer"
      Tier        = "Web"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Security Group: Web Tier EC2 Instances
# Purpose: Control traffic to web/application servers behind ALB
# Used by: Compute module for Auto Scaling Group instances
resource "aws_security_group" "web_tier" {
  name_prefix = "${var.project_name}-web-"
  description = "Security group for web tier EC2 instances - only accessible from ALB"
  vpc_id      = aws_vpc.main.id

  # Allow HTTP from ALB security group only
  # This ensures instances are ONLY accessible through the load balancer
  ingress {
    description     = "HTTP from Application Load Balancer"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]  # Source: ALB SG (not CIDR)
  }

  # Allow HTTPS from ALB (if serving HTTPS on instances)
  # Typically SSL terminates at ALB, instances serve HTTP
  # Uncomment if end-to-end encryption required
  /*
  ingress {
    description     = "HTTPS from Application Load Balancer"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  */

  # Allow SSH from bastion (if bastion exists)
  # Alternatively, use SSM Session Manager (no SSH needed)
  # Commented out - use SSM endpoints instead
  /*
  ingress {
    description     = "SSH from bastion host"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
  */

  # Allow all outbound traffic
  # Instances need: Internet via NAT (yum updates), RDS database, S3, etc.
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-web-tier-sg"
      Description = "Security group for web tier instances"
      Tier        = "Application"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Security Group: RDS Database
# Purpose: Control access to RDS instances
# Used by: Database module for PostgreSQL RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  description = "Security group for RDS database - only accessible from application tier"
  vpc_id      = aws_vpc.main.id

  # Allow PostgreSQL from web tier security group
  # Port 5432 is PostgreSQL default
  ingress {
    description     = "PostgreSQL from web/app tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]  # Only from app servers
  }

  # Allow PostgreSQL from app tier security group (if separate)
  # Uncomment if you have separate web and app tiers
  /*
  ingress {
    description     = "PostgreSQL from application tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }
  */

  # Allow PostgreSQL from bastion for DB administration
  # Commented out - use RDS Query Editor or SSH tunnel instead
  /*
  ingress {
    description     = "PostgreSQL from bastion for admin access"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
  */

  # RDS typically needs no outbound access
  # But egress rules required for RDS enhanced monitoring
  egress {
    description = "Allow outbound for RDS enhanced monitoring"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-rds-sg"
      Description = "Security group for RDS database"
      Tier        = "Database"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Security Group: Bastion Host (Optional)
# Purpose: Secure jump box for administrative access
# Note: With SSM Session Manager, bastion hosts are largely unnecessary
# Include only if: SSM not available, compliance requires SSH bastion, hybrid connectivity
resource "aws_security_group" "bastion" {
  count       = var.enable_bastion_sg ? 1 : 0
  name_prefix = "${var.project_name}-bastion-"
  description = "Security group for bastion host - SSH from specific IPs only"
  vpc_id      = aws_vpc.main.id

  # Allow SSH from specific IP ranges (corporate office, home IP, VPN)
  # NEVER use 0.0.0.0/0 for SSH - massive security risk
  ingress {
    description = "SSH from trusted IP ranges"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.bastion_allowed_cidrs  # Variable for flexibility
  }

  # Allow all outbound (bastion needs to reach instances, RDS for tunneling)
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-bastion-sg"
      Description = "Security group for bastion host"
      Tier        = "Management"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Variable for bastion allowed CIDRs
variable "enable_bastion_sg" {
  description = "Create security group for bastion host. Set false if using SSM Session Manager."
  type        = bool
  default     = false
}

variable "bastion_allowed_cidrs" {
  description = <<-EOT
    List of CIDR blocks allowed to SSH to bastion host.
    Example: ["203.0.113.0/24", "198.51.100.0/24"]
    NEVER use ["0.0.0.0/0"] - this allows SSH from anywhere (security risk)
  EOT
  type        = list(string)
  default     = []  # Must be explicitly set if bastion enabled
}

# Security Group: ElastiCache (Optional, for Redis/Memcached)
# Purpose: Control access to ElastiCache clusters
resource "aws_security_group" "elasticache" {
  count       = var.enable_elasticache_sg ? 1 : 0
  name_prefix = "${var.project_name}-elasticache-"
  description = "Security group for ElastiCache - Redis/Memcached access from app tier"
  vpc_id      = aws_vpc.main.id

  # Allow Redis from web/app tier
  ingress {
    description     = "Redis from application tier"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }

  # Allow Memcached from web/app tier
  ingress {
    description     = "Memcached from application tier"
    from_port       = 11211
    to_port         = 11211
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-elasticache-sg"
      Description = "Security group for ElastiCache"
      Tier        = "Cache"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

variable "enable_elasticache_sg" {
  description = "Create security group for ElastiCache. Enable if using Redis or Memcached."
  type        = bool
  default     = false
}

# Outputs for security groups

output "alb_security_group_id" {
  description = "Security group ID for Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "web_tier_security_group_id" {
  description = "Security group ID for web tier instances"
  value       = aws_security_group.web_tier.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS database"
  value       = aws_security_group.rds.id
}

output "bastion_security_group_id" {
  description = "Security group ID for bastion host (if enabled)"
  value       = length(aws_security_group.bastion) > 0 ? aws_security_group.bastion[0].id : null
}

output "elasticache_security_group_id" {
  description = "Security group ID for ElastiCache (if enabled)"
  value       = length(aws_security_group.elasticache) > 0 ? aws_security_group.elasticache[0].id : null
}
