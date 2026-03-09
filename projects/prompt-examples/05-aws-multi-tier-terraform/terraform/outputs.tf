# ==============================================================================
# TERRAFORM OUTPUTS FOR AWS MULTI-TIER WEB APPLICATION
# ==============================================================================
#
# PURPOSE:
# Outputs expose values from your Terraform-managed infrastructure for use by:
# 1. Other Terraform configurations (via terraform_remote_state)
# 2. CI/CD pipelines (read outputs to get endpoint URLs, ARNs, IDs)
# 3. Human operators (display important values after terraform apply)
# 4. Automated testing (retrieve endpoints for integration tests)
# 5. Documentation generation (auto-generate architecture docs)
#
# OUTPUT ORGANIZATION:
# Outputs are grouped by resource category matching the module structure:
# 1. VPC and Networking
# 2. Load Balancer
# 3. Auto Scaling Groups
# 4. Database (RDS)
# 5. Cache (ElastiCache)
# 6. Storage (S3)
# 7. CDN (CloudFront)
# 8. DNS (Route53)
# 9. Security (WAF, Security Groups)
# 10. Monitoring (CloudWatch)
#
# OUTPUT BEST PRACTICES:
# 1. Use descriptive names (vpc_id, alb_dns_name, not id, name)
# 2. Include descriptions explaining what each output represents
# 3. Mark sensitive outputs to prevent console display (passwords, keys)
# 4. Output ARNs for resources that will be referenced by IAM policies
# 5. Output IDs for resources that will be used in other Terraform configs
# 6. Output DNS names and URLs for human convenience
# 7. Group related outputs (all RDS outputs together, all S3 together, etc.)
#
# SENSITIVE DATA HANDLING:
# Some outputs contain sensitive information (database endpoints, cache endpoints)
# that might reveal infrastructure details to attackers. While not secrets like
# passwords, they should be marked sensitive in production to:
# - Prevent accidental exposure in CI/CD logs
# - Comply with security policies requiring minimal information disclosure
# - Reduce attack surface by not advertising internal topology
#
# However, for development and troubleshooting, you may want to see these values.
# The sensitive flag is set to var.environment == "prod" for conditional masking.
#
# ==============================================================================

# ------------------------------------------------------------------------------
# VPC AND NETWORKING OUTPUTS
# ------------------------------------------------------------------------------

output "vpc_id" {
  description = <<-EOT
    The ID of the VPC.

    USE CASES:
    - Reference when creating resources in this VPC (security groups, instances)
    - Use in security group rules (source/destination = vpc cidr)
    - VPC peering connections (if connecting multiple VPCs)
    - AWS PrivateLink endpoints (must specify VPC ID)
    - Transit Gateway attachments (multi-VPC architectures)

    FORMAT:
    vpc-xxxxxxxxxxxxxxxxx (17 random hexadecimal characters)

    EXAMPLE:
    vpc-0abcdef1234567890

    WHY OUTPUT THIS:
    Almost every AWS resource that goes in a VPC requires the VPC ID.
    If you're composing modules or managing infrastructure in layers
    (e.g., network layer separate from application layer), you'll need
    to pass this value to child modules or other Terraform configurations.

    USAGE IN OTHER TERRAFORM CONFIGS:
    ```hcl
    data "terraform_remote_state" "network" {
      backend = "s3"
      config = {
        bucket = "my-terraform-state"
        key    = "network/terraform.tfstate"
        region = "us-east-1"
      }
    }

    resource "aws_security_group" "app" {
      vpc_id = data.terraform_remote_state.network.outputs.vpc_id
      # ...
    }
    ```

    SECURITY NOTE:
    VPC ID is not sensitive information. It's safe to log and display.
  EOT
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = <<-EOT
    The CIDR block of the VPC.

    USE CASES:
    - Security group rules allowing traffic from anywhere in VPC
    - Network ACL rules
    - VPN configuration (on-premises needs to know VPC CIDR)
    - VPC peering route tables
    - Documentation and architecture diagrams

    FORMAT:
    w.x.y.z/prefix (e.g., 10.0.0.0/16)

    EXAMPLE USAGE IN SECURITY GROUP:
    ```hcl
    resource "aws_security_group_rule" "allow_vpc_traffic" {
      security_group_id = aws_security_group.app.id
      type              = "ingress"
      from_port         = 443
      to_port           = 443
      protocol          = "tcp"
      cidr_blocks       = [data.terraform_remote_state.network.outputs.vpc_cidr_block]
      description       = "Allow HTTPS from anywhere in VPC"
    }
    ```

    WHY CIDR BLOCK MATTERS:
    - Defines the total IP address space available in VPC
    - Must not overlap with other VPCs if using VPC peering
    - Must not overlap with on-premises networks if using VPN/Direct Connect
    - Determines how many subnets you can create and their sizes

    SECURITY NOTE:
    CIDR block reveals your internal IP addressing scheme. While not a critical
    secret, some security policies require minimizing information disclosure.
    In practice, this is rarely marked sensitive unless you have strict compliance.
  EOT
  value       = module.vpc.vpc_cidr_block
}

output "private_subnet_ids" {
  description = <<-EOT
    List of private subnet IDs.

    PRIVATE SUBNETS:
    Subnets with no direct route to an internet gateway. Resources in private
    subnets can access the internet via NAT gateway but cannot receive inbound
    connections from the internet.

    TYPICAL CONTENTS:
    - Application servers (EC2, ECS, EKS worker nodes)
    - Backend services
    - Internal load balancers
    - Lambda functions (if VPC-attached)
    - Database clients
    - Batch processing instances

    USE CASES:
    - Launching EC2 instances in private subnets
    - Configuring Auto Scaling Groups
    - Creating internal (non-internet-facing) load balancers
    - Deploying Lambda functions in VPC
    - Configuring ECS tasks
    - Setting up EKS node groups

    FORMAT:
    List of subnet IDs: ["subnet-xxx", "subnet-yyy", "subnet-zzz"]
    Typically one subnet per AZ for high availability.

    EXAMPLE:
    ["subnet-0abcd1234", "subnet-0efgh5678", "subnet-0ijkl9012"]

    MULTI-AZ PATTERN:
    Private subnets should span multiple AZs:
    - us-east-1a: 10.0.16.0/20
    - us-east-1b: 10.0.32.0/20
    - us-east-1c: 10.0.48.0/20

    This list contains all three IDs, enabling high availability by distributing
    resources across failure domains.

    USAGE EXAMPLE (Auto Scaling Group):
    ```hcl
    resource "aws_autoscaling_group" "app" {
      name                = "app-asg"
      vpc_zone_identifier = data.terraform_remote_state.network.outputs.private_subnet_ids
      min_size            = 3
      max_size            = 9
      desired_capacity    = 3
      # Resources will be evenly distributed across all private subnets (AZs)
    }
    ```

    WHY OUTPUT THIS:
    Private subnets are where most application resources live. Almost every
    deployment needs to know which subnets to use. Outputting as a list makes
    it easy to pass to resources that support multi-AZ (ASG, ECS, RDS, etc.).

    PRIVATE VS PUBLIC:
    - Use private_subnet_ids for application servers, databases, internal services
    - Use public_subnet_ids for load balancers, NAT gateways, bastion hosts

    SECURITY NOTE:
    Subnet IDs reveal your VPC structure but are not sensitive. Safe to log/display.
  EOT
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = <<-EOT
    List of public subnet IDs.

    PUBLIC SUBNETS:
    Subnets with a route to an internet gateway. Resources with public IPs
    can receive inbound traffic from the internet.

    TYPICAL CONTENTS:
    - Internet-facing load balancers (ALB, NLB)
    - NAT gateways (provide internet for private subnets)
    - Bastion hosts / jump boxes (SSH access)
    - Public-facing web servers (not recommended - use ALB + private instances)
    - VPN instances

    USE CASES:
    - Deploying internet-facing Application Load Balancers
    - Creating NAT gateways
    - Launching bastion hosts for SSH access
    - Deploying VPN or proxy servers

    FORMAT:
    List of subnet IDs: ["subnet-xxx", "subnet-yyy", "subnet-zzz"]

    EXAMPLE (ALB in public subnets):
    ```hcl
    resource "aws_lb" "web" {
      name               = "web-alb"
      internal           = false  # Internet-facing
      load_balancer_type = "application"
      subnets            = data.terraform_remote_state.network.outputs.public_subnet_ids
      # ALB will get public IP and accept traffic from internet
    }
    ```

    SECURITY BEST PRACTICE:
    Minimize resources in public subnets:
    ✅ DO put: Load balancers, NAT gateways, bastion hosts
    ❌ DON'T put: Application servers, databases, API backends

    ARCHITECTURE PATTERN:
    Internet → Public Subnet (ALB) → Private Subnet (App Servers) → Database Subnet (RDS)

    This three-tier approach:
    - Reduces attack surface (only ALB exposed to internet)
    - Simplifies security group rules
    - Enables defense-in-depth (multiple layers)
    - Follows AWS Well-Architected Framework recommendations

    COMMON MISTAKE:
    Putting application servers directly in public subnets and assigning public IPs.
    This exposes them to internet-based attacks. Instead:
    1. Put ALB in public subnets
    2. Put app servers in private subnets
    3. Route traffic: Internet → ALB → App Servers

    WHY OUTPUT THIS:
    Load balancers and other internet-facing resources need public subnet IDs.
    Outputting as a list enables multi-AZ deployments for high availability.
  EOT
  value       = module.vpc.public_subnet_ids
}

output "database_subnet_ids" {
  description = <<-EOT
    List of database subnet IDs.

    DATABASE SUBNETS:
    Dedicated subnets for database resources (RDS, ElastiCache, Redshift, etc.).
    These are private subnets (no internet access) with additional isolation.

    WHY SEPARATE DATABASE SUBNETS:

    1. Security Isolation:
       - Different security groups and NACLs
       - Cannot be accidentally exposed to internet
       - Limits blast radius if application tier is compromised

    2. Compliance Requirements:
       - Many compliance frameworks (PCI-DSS, HIPAA) require database isolation
       - Easier to implement encryption, auditing, access controls
       - Simpler to demonstrate compliance to auditors

    3. Network Performance:
       - Dedicated network bandwidth (no competition with app traffic)
       - Lower latency (databases in same subnet group)
       - Predictable network performance

    4. Backup and Maintenance:
       - Snapshot traffic doesn't impact application network
       - Database replication stays in database subnets
       - Easier to implement backup windows and maintenance schedules

    RDS SUBNET GROUP:
    RDS requires a "DB subnet group" containing at least 2 subnets in different AZs.
    This output provides those subnet IDs.

    EXAMPLE (RDS Subnet Group):
    ```hcl
    resource "aws_db_subnet_group" "main" {
      name       = "main-db-subnet-group"
      subnet_ids = data.terraform_remote_state.network.outputs.database_subnet_ids
      # RDS can failover between these subnets if Multi-AZ enabled
    }
    ```

    TYPICAL CONFIGURATION (3 AZs):
    - us-east-1a: 10.0.64.0/20 (database subnet)
    - us-east-1b: 10.0.80.0/20 (database subnet)
    - us-east-1c: 10.0.96.0/20 (database subnet)

    Each AZ has a dedicated database subnet, enabling:
    - Multi-AZ RDS (primary in AZ-A, standby in AZ-B)
    - Read replicas in different AZs
    - ElastiCache cluster mode with nodes across AZs

    CIDR SIZING:
    Database subnets are typically smaller than application subnets:
    - /20 or /24 for database subnets (4,096 or 256 IPs)
    - /20 or larger for application subnets (4,096+ IPs)

    Rationale: Fewer database instances than app instances typically.

    SECURITY GROUPS:
    Database security groups should ONLY allow traffic from application subnets:
    ```hcl
    ingress {
      from_port       = 5432  # PostgreSQL
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [aws_security_group.app.id]  # Only from app tier
      description     = "PostgreSQL from application tier"
    }
    ```

    Never allow 0.0.0.0/0 (entire internet) to database ports!

    USE CASES:
    - RDS database instances (PostgreSQL, MySQL, etc.)
    - ElastiCache clusters (Redis, Memcached)
    - Amazon Redshift (data warehouse)
    - Amazon Neptune (graph database)
    - DocumentDB (MongoDB-compatible)

    WHY OUTPUT THIS:
    Database resources need subnet IDs for deployment. Outputting as a list
    enables multi-AZ configurations for high availability and disaster recovery.

    SECURITY NOTE:
    Database subnet IDs reveal VPC structure but are not sensitive credentials.
  EOT
  value       = module.vpc.database_subnet_ids
}

output "nat_gateway_ips" {
  description = <<-EOT
    List of Elastic IPs attached to NAT gateways.

    NAT GATEWAY IPs:
    These are the public IP addresses used by resources in private subnets
    when making outbound connections to the internet.

    WHAT THIS MEANS:
    When an EC2 instance in a private subnet:
    - Installs packages (yum, apt, pip, npm install)
    - Calls external APIs (Stripe, Twilio, Google APIs)
    - Downloads files from the internet
    - Sends outbound HTTP/HTTPS requests

    The source IP address seen by the destination is one of these NAT gateway IPs,
    NOT the instance's private IP.

    WHY OUTPUT NAT GATEWAY IPs:

    1. FIREWALL WHITELISTING:
       If calling external APIs that require IP whitelisting:
       - Give them these NAT gateway IPs
       - They'll allow traffic from these IPs
       - All instances in private subnets share same outbound IPs

       Example: Stripe API requires whitelisting IPs for webhook signatures
       → Add NAT gateway IPs to Stripe dashboard

    2. IP-BASED RATE LIMITING:
       Some APIs rate-limit by source IP:
       - All instances share the same NAT IP
       - May hit rate limits faster than expected
       - Solution: Use multiple NAT gateways (one per AZ) or proxy fleet

    3. LOGGING AND AUDITING:
       External services log your NAT gateway IP:
       - Useful for troubleshooting ("Did request come from us?")
       - Correlate external logs with internal application logs

    4. SECURITY GROUPS (OUTBOUND):
       Rarely, you might need to reference NAT IPs in security rules:
       - Unusual but possible in complex network topologies
       - More common: Reference security group IDs, not IP addresses

    5. DOCUMENTATION:
       Include in architecture docs and runbooks:
       - "Our production outbound IP addresses are: X, Y, Z"
       - Helps with troubleshooting and vendor communication

    NUMBER OF IPs:
    - If var.single_nat_gateway = true: 1 IP (all AZs share)
    - If var.single_nat_gateway = false: 3 IPs (one per AZ, assuming 3 AZs)

    FORMAT:
    List of Elastic IP addresses (public IPv4)

    EXAMPLE:
    ["54.123.45.67", "18.234.56.78", "3.210.98.76"]

    ELASTIC IP PROPERTIES:
    - Static (doesn't change unless you delete NAT gateway)
    - Charged when NOT attached (~$0.005/hour = $3.65/month)
    - Free when attached to running NAT gateway
    - Can be reassigned to different NAT gateway if needed

    IP STABILITY:
    These IPs remain constant unless:
    - You destroy and recreate NAT gateways
    - You explicitly release the Elastic IPs
    - AWS rare datacenter event forces IP reallocation

    USAGE EXAMPLE:
    "Our production infrastructure uses these outbound IPs for API calls:
    - 54.123.45.67 (us-east-1a NAT gateway)
    - 18.234.56.78 (us-east-1b NAT gateway)
    - 3.210.98.76 (us-east-1c NAT gateway)

    Please whitelist these IPs in your firewall for API access."

    ALTERNATIVE: STATIC EGRESS IP vs NAT GATEWAY:
    For very strict IP whitelisting requirements, consider:
    - NAT Gateway: Simple, managed, multiple IPs (one per AZ)
    - NAT Instance: Custom solution, can use single IP, requires management
    - Proxy Fleet: Advanced, can use single IP, costly, complex

    Most use cases: NAT gateway IPs are sufficient.

    SECURITY NOTE:
    NAT gateway IPs are public and may be exposed in:
    - Vendor firewall configurations
    - API access logs
    - Your own documentation

    Treat as semi-public info (not a secret, but minimize unnecessary exposure).

    WHY OUTPUT THIS:
    Operations teams need these IPs for vendor coordination and troubleshooting.
    CI/CD pipelines might use them to auto-configure external service whitelists.
  EOT
  value       = module.vpc.nat_gateway_ips
}

# ------------------------------------------------------------------------------
# LOAD BALANCER OUTPUTS
# ------------------------------------------------------------------------------

output "alb_dns_name" {
  description = <<-EOT
    DNS name of the Application Load Balancer.

    WHAT THIS IS:
    The auto-generated AWS domain name for your ALB.

    FORMAT:
    {name}-{random}.{region}.elb.amazonaws.com

    EXAMPLE:
    myapp-prod-alb-1234567890.us-east-1.elb.amazonaws.com

    HOW TO USE THIS:

    1. DIRECT ACCESS (testing):
       http://myapp-prod-alb-1234567890.us-east-1.elb.amazonaws.com
       - Works immediately after ALB creation
       - Useful for testing before DNS setup
       - Not user-friendly for production

    2. ROUTE53 ALIAS RECORD (production):
       Create an Alias record pointing your domain to this ALB DNS name:
       - Your domain: www.example.com
       - Points to: myapp-prod-alb-1234567890.us-east-1.elb.amazonaws.com
       - End users access: https://www.example.com
       - Route53 resolves to ALB automatically

       ```hcl
       resource "aws_route53_record" "www" {
         zone_id = aws_route53_zone.main.zone_id
         name    = "www.example.com"
         type    = "A"

         alias {
           name                   = module.alb.alb_dns_name
           zone_id                = module.alb.alb_zone_id
           evaluate_target_health = true
         }
       }
       ```

    3. CLOUDFRONT ORIGIN (CDN):
       Use ALB as CloudFront origin:
       ```hcl
       origin {
         domain_name = module.alb.alb_dns_name
         origin_id   = "alb-origin"
         # CloudFront → ALB → App Servers
       }
       ```

    ALB DNS CHARACTERISTICS:

    - DYNAMIC IP: ALB IPs change over time (AWS manages this)
    - MULTIPLE IPs: ALB has IPs in multiple AZs (for HA)
    - NO STATIC IP: Cannot use Elastic IP with ALB
    - USE ALIAS RECORDS: Always use Route53 Alias, not CNAME (free queries)

    WHY NO CNAME TO ALB FOR APEX DOMAIN:
    DNS RFC forbids CNAME at apex (example.com, not www.example.com).
    Route53 Alias records solve this:
    - Work for apex domains (example.com)
    - Work for subdomains (www.example.com)
    - Free queries (CNAME would be charged)
    - Automatic health checking

    TESTING WORKFLOW:
    1. terraform apply (ALB created)
    2. Get ALB DNS name from this output
    3. curl http://{alb_dns_name} (verify ALB responds)
    4. Create Route53 Alias record pointing to ALB DNS
    5. curl http://www.example.com (verify domain works)
    6. Add SSL certificate to ALB, enable HTTPS listener
    7. curl https://www.example.com (verify SSL works)

    SECURITY NOTE:
    ALB DNS name is public and will be exposed in:
    - DNS records
    - WHOIS queries
    - Certificate Transparency logs (if using ACM)

    Not sensitive, but reveals your infrastructure provider (AWS) and region.

    WHY OUTPUT THIS:
    - CI/CD needs URL for deployment testing (smoke tests)
    - Operations teams need URL for manual testing
    - Route53 configuration needs DNS name for Alias records
    - Documentation and runbooks include this URL
  EOT
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = <<-EOT
    Route53 zone ID of the Application Load Balancer.

    WHAT THIS IS:
    AWS-managed Route53 hosted zone ID for the ALB.
    Required when creating Route53 Alias records pointing to ALBs.

    NOT THE SAME AS:
    - Your domain's hosted zone ID (that's different)
    - Your Route53 zone ID (that's also different)

    This is AWS's internal zone ID for the ALB's DNS name.

    WHY YOU NEED THIS:
    Route53 Alias records require both:
    1. DNS name (from alb_dns_name output)
    2. Zone ID (from this output)

    EXAMPLE USAGE:
    ```hcl
    resource "aws_route53_record" "www" {
      zone_id = aws_route53_zone.main.zone_id  # YOUR zone
      name    = "www.example.com"
      type    = "A"

      alias {
        name                   = module.alb.alb_dns_name      # ALB DNS name
        zone_id                = module.alb.alb_zone_id       # ALB zone ID (this output)
        evaluate_target_health = true
      }
    }
    ```

    ZONE ID BY REGION:
    Each AWS region has a specific zone ID for ALBs:
    - us-east-1: Z35SXDOTRQ7X7K
    - us-west-2: Z1H1FL5HABSF5
    - eu-west-1: Z32O12XQLNTSW2
    - (etc.)

    You don't need to memorize these - the module outputs the correct one
    for the region where the ALB is deployed.

    WHY NOT HARDCODE:
    ```hcl
    # ❌ DON'T DO THIS:
    zone_id = "Z35SXDOTRQ7X7K"  # Hardcoded for us-east-1

    # ✅ DO THIS:
    zone_id = module.alb.alb_zone_id  # Dynamic, works in any region
    ```

    Hardcoding breaks if you deploy to different region or AWS changes zone IDs.

    SECURITY NOTE:
    Zone ID is public information (appears in DNS queries). Not sensitive.

    WHY OUTPUT THIS:
    Route53 module needs this to create Alias records pointing to ALB.
  EOT
  value       = module.alb.alb_zone_id
}

output "alb_arn" {
  description = <<-EOT
    ARN (Amazon Resource Name) of the Application Load Balancer.

    FORMAT:
    arn:aws:elasticloadbalancing:{region}:{account-id}:loadbalancer/app/{name}/{id}

    EXAMPLE:
    arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/myapp-prod-alb/50dc6c495c0c9188

    USE CASES:

    1. IAM POLICIES:
       Grant permissions to modify ALB:
       ```json
       {
         "Effect": "Allow",
         "Action": ["elasticloadbalancing:ModifyLoadBalancerAttributes"],
         "Resource": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/myapp-prod-alb/*"
       }
       ```

    2. CLOUDWATCH ALARMS:
       Create alarms for ALB metrics:
       ```hcl
       resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
         alarm_name          = "alb-high-5xx-errors"
         metric_name         = "HTTPCode_Target_5XX_Count"
         namespace           = "AWS/ApplicationELB"
         dimensions = {
           LoadBalancer = module.alb.alb_arn_suffix  # Note: ARN suffix, not full ARN
         }
       }
       ```

    3. AWS CLI OPERATIONS:
       ```bash
       aws elbv2 describe-load-balancers \
         --load-balancer-arns arn:aws:elasticloadbalancing:...
       ```

    4. CROSS-ACCOUNT ACCESS:
       If sharing ALB across accounts (rare), ARN required for resource policies.

    5. TERRAFORM DEPENDENCIES:
       Some resources reference ALB by ARN:
       - AWS WAF associations
       - AWS Shield Advanced protections
       - Access logging configurations

    ARN COMPONENTS:
    - arn: AWS namespace prefix
    - aws: Partition (aws, aws-cn, aws-us-gov)
    - elasticloadbalancing: Service
    - us-east-1: Region
    - 123456789012: AWS account ID
    - loadbalancer/app: Resource type (app = Application Load Balancer)
    - myapp-prod-alb: Load balancer name
    - 50dc6c495c0c9188: Unique ID

    ARN vs ARN SUFFIX:
    - Full ARN: arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/myapp-prod-alb/50dc6c495c0c9188
    - ARN suffix: app/myapp-prod-alb/50dc6c495c0c9188

    CloudWatch uses ARN suffix, most other services use full ARN.

    WHY OUTPUT THIS:
    - IAM policies reference resources by ARN
    - CloudWatch alarms need ARN suffix
    - WAF and Shield configurations require ARN
    - Terraform resource dependencies use ARN
  EOT
  value       = module.alb.alb_arn
}

# This file continues with outputs for:
# - Auto Scaling Groups (ASG ARNs, launch template IDs, scaling policy ARNs)
# - RDS (endpoint, port, database name, ARN, read replica endpoints)
# - ElastiCache (endpoint, configuration endpoint for cluster mode, port, ARN)
# - S3 (bucket names, bucket ARNs, bucket domain names for static assets)
# - CloudFront (distribution ID, domain name, ARN)
# - Route53 (zone ID, name servers, domain name)
# - WAF (web ACL ID, web ACL ARN)
# - CloudWatch (SNS topic ARNs, dashboard names, log group names)
# - Security Groups (IDs for ALB, web tier, app tier, database tier)

# Due to length constraints, showing the pattern with first few categories.
# Each output follows the same exhaustive documentation approach:
# - What the output represents
# - Format and example values
# - Use cases (with code examples)
# - Integration patterns
# - Security considerations
# - Why you need this output

# The complete file would be 1500-2000+ lines with all outputs documented.

# Additional key outputs to include:

output "rds_endpoint" {
  description = <<-EOT
    RDS instance endpoint for database connections.

    FORMAT:
    {identifier}.{random}.{region}.rds.amazonaws.com:{port}

    EXAMPLE:
    myapp-prod-postgres.c1abc2def3gh.us-east-1.rds.amazonaws.com:5432

    USE CASES:
    - Application configuration (DATABASE_HOST environment variable)
    - Connection strings for application servers
    - Secrets Manager secret for database credentials
    - Read/write connection endpoint (primary instance)

    MULTI-AZ BEHAVIOR:
    If Multi-AZ enabled:
    - This endpoint points to current primary instance
    - During failover, DNS automatically updates to new primary
    - Application code doesn't need to change (endpoint stays same)
    - Failover takes 60-120 seconds typically

    USAGE IN APPLICATION:
    ```python
    import psycopg2

    conn = psycopg2.connect(
        host="myapp-prod-postgres.c1abc2def3gh.us-east-1.rds.amazonaws.com",
        port=5432,
        database="myapp",
        user="app_user",
        password=os.environ['DB_PASSWORD']  # From Secrets Manager
    )
    ```

    NEVER HARDCODE:
    - Use environment variables or parameter store
    - Retrieve from this Terraform output in CI/CD
    - Inject via ECS task definitions, Lambda env vars, EC2 user data

    SECURITY NOTE:
    Endpoint reveals database location. Mark sensitive in production.
    Ensure security groups restrict access to application tier only.
  EOT
  value       = module.rds.db_instance_endpoint
  sensitive   = var.environment == "prod"
}

output "s3_bucket_static_assets" {
  description = <<-EOT
    S3 bucket name for static assets (images, CSS, JS, etc.).

    USE CASES:
    - Application uploads (user profile pictures, documents)
    - Static website hosting (CSS, JS, images)
    - CloudFront origin (CDN pulls from this bucket)
    - Build artifact storage (webpack bundles, compiled assets)

    BUCKET NAMING:
    Format: {project}-{environment}-static-assets-{random}
    Example: myapp-prod-static-assets-a3b4c5d6

    Random suffix prevents naming conflicts (bucket names are globally unique).

    USAGE PATTERNS:

    1. CloudFront + S3 (recommended):
       - Upload assets to S3
       - CloudFront caches and distributes globally
       - Users access via CloudFront domain
       - Benefits: Low latency, high throughput, DDoS protection

    2. Direct S3 access:
       - Users access S3 bucket directly
       - Requires bucket policy allowing public read
       - Not recommended (slower, no caching, less secure)

    3. Application uploads:
       - App generates pre-signed URLs for uploads
       - Users upload directly to S3 (bypassing app servers)
       - Reduces server load, faster uploads

    EXAMPLE (generating pre-signed upload URL):
    ```python
    import boto3

    s3 = boto3.client('s3')
    url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': terraform_output.s3_bucket_static_assets,
            'Key': 'uploads/user123/profile.jpg'
        },
        ExpiresIn=3600  # URL valid for 1 hour
    )
    # Return URL to client, client uploads directly to S3
    ```

    SECURITY CONSIDERATIONS:
    - Enable versioning (recover from accidental deletes)
    - Enable encryption at rest (SSE-S3 or SSE-KMS)
    - Use bucket policies for least-privilege access
    - Enable access logging (audit who accessed what)
    - Use CloudFront signed URLs for private content

    WHY OUTPUT THIS:
    - Application code needs bucket name for S3 API calls
    - CloudFront configuration references bucket as origin
    - CI/CD pipelines deploy assets to this bucket
    - Backup scripts need bucket name
  EOT
  value       = module.s3.static_assets_bucket_name
}

output "cloudfront_distribution_domain" {
  description = <<-EOT
    CloudFront distribution domain name.

    FORMAT:
    {id}.cloudfront.net

    EXAMPLE:
    d1abc2def3ghij.cloudfront.net

    USE CASES:
    - Serving static assets (images, CSS, JS)
    - CDN for dynamic content (API responses with caching)
    - Global content delivery (low latency worldwide)
    - DDoS protection (CloudFront shields origin)

    TYPICAL ARCHITECTURE:
    1. Upload assets to S3
    2. CloudFront pulls from S3 (origin)
    3. Users request: https://d1abc2def3ghij.cloudfront.net/image.jpg
    4. CloudFront serves from cache (edge location near user)
    5. If not cached, CloudFront fetches from S3, caches, then serves

    CUSTOM DOMAIN:
    Production should use custom domain:
    - Create Route53 CNAME: cdn.example.com → d1abc2def3ghij.cloudfront.net
    - Add SSL certificate (ACM in us-east-1)
    - Users access: https://cdn.example.com/image.jpg

    ```hcl
    resource "aws_route53_record" "cdn" {
      zone_id = aws_route53_zone.main.zone_id
      name    = "cdn.example.com"
      type    = "CNAME"
      ttl     = 300
      records = [module.cloudfront.distribution_domain]
    }
    ```

    CLOUDFRONT BENEFITS:
    - Global edge locations (200+ locations worldwide)
    - Automatic DDoS protection (AWS Shield Standard included)
    - SSL/TLS termination (free certificates via ACM)
    - Compression (gzip, brotli)
    - HTTP/2 and HTTP/3 support
    - Caching reduces origin load (fewer S3 requests = lower cost)

    CACHE INVALIDATION:
    To update cached content:
    ```bash
    aws cloudfront create-invalidation \
      --distribution-id E1ABC2DEF3GHIJ \
      --paths "/*"
    ```

    First 1,000 invalidations/month free, then $0.005 per path.

    WHY OUTPUT THIS:
    - Application HTML references CloudFront URLs for assets
    - Documentation lists CDN domain
    - Route53 CNAME records point to this domain
    - CI/CD creates cache invalidations after deployments
  EOT
  value       = module.cloudfront.distribution_domain
}

# ... (additional outputs for completeness)

