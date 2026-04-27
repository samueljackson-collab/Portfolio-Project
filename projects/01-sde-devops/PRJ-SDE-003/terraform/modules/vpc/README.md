# VPC Module

Production-ready AWS VPC module for three-tier web application architecture with high availability, security, and operational excellence.

## Features

### Network Architecture
- **Multi-AZ Deployment**: Subnets across 2-3 availability zones for high availability
- **Three-Tier Subnet Strategy**:
  - Public subnets: ALB, NAT Gateways, Bastion (optional)
  - Private application subnets: EC2 instances, ECS tasks, Lambda
  - Private database subnets: RDS, ElastiCache, Redshift (completely isolated)
- **CIDR Planning**: Flexible /16 VPC with /24 subnets (easily accommodates 100+ hosts per tier per AZ)

### Connectivity
- **Internet Gateway**: Public subnet internet access
- **NAT Gateways**: Private subnet outbound internet access
  - High Availability mode: One NAT per AZ (~$100/month)
  - Cost-optimized mode: Single NAT Gateway (~$32/month)
- **VPC Endpoints**: Private AWS service access without NAT
  - S3 & DynamoDB: Gateway endpoints (FREE)
  - ECR: Interface endpoints for container image pulls (~$22/month)
  - SSM: Systems Manager for SSH-less instance management (~$22/month)

### Security
- **Security Groups**: Pre-configured for ALB, web tier, database, bastion
- **VPC Flow Logs**: Network traffic monitoring for security and troubleshooting
- **Network ACLs**: Optional subnet-level firewall rules
- **Private Subnets**: Database tier completely isolated from internet

### Operational Excellence
- **Terraform State**: S3 backend with DynamoDB locking
- **Modular Design**: Reusable across environments (dev/staging/prod)
- **Comprehensive Tagging**: Cost allocation, automation, compliance
- **CloudWatch Integration**: Flow logs, VPC metrics, endpoint monitoring

## Usage

### Basic Example (Development Environment)
```hcl
module "vpc" {
  source = "../../modules/vpc"

  project_name = "myapp"
  environment  = "dev"
  vpc_cidr     = "10.0.0.0/16"

  # Cost optimization for dev
  enable_nat_gateway     = true
  single_nat_gateway     = true   # Single NAT to save $66/month
  enable_flow_logs       = false  # Disable to save CloudWatch costs
  enable_ssm_endpoints   = true   # SSH-less access
  enable_s3_endpoint     = true   # Free, always enable
  enable_ecr_endpoints   = false  # Disable if not using containers

  common_tags = {
    Project     = "MyApplication"
    Environment = "Development"
    Owner       = "DevOps Team"
    CostCenter  = "Engineering"
    Terraform   = "true"
  }
}
```

### Production Example (High Availability)
```hcl
module "vpc" {
  source = "../../modules/vpc"

  project_name = "myapp"
  environment  = "prod"
  vpc_cidr     = "10.0.0.0/16"

  # High availability configuration
  enable_nat_gateway        = true
  single_nat_gateway        = false  # One NAT per AZ for redundancy
  enable_flow_logs          = true   # Security and compliance
  flow_logs_retention_days  = 30     # Retain for audit
  enable_ssm_endpoints      = true   # Secure management
  enable_s3_endpoint        = true
  enable_dynamodb_endpoint  = true   # If using DynamoDB
  enable_ecr_endpoints      = true   # If using ECS/EKS

  common_tags = {
    Project     = "MyApplication"
    Environment = "Production"
    Owner       = "DevOps Team"
    CostCenter  = "Production-Infra"
    Terraform   = "true"
    Compliance  = "SOC2"
  }
}
```

### Accessing Outputs
```hcl
# In other modules or root configuration
resource "aws_instance" "app" {
  subnet_id              = module.vpc.private_app_subnet_ids[0]  # First AZ
  vpc_security_group_ids = [module.vpc.web_tier_security_group_id]
  
  # ... other configuration
}

resource "aws_db_instance" "main" {
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [module.vpc.rds_security_group_id]
  
  # ... other configuration
}

resource "aws_db_subnet_group" "main" {
  name       = "myapp-db-subnet-group"
  subnet_ids = module.vpc.private_db_subnet_ids  # All AZs
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| project_name | Project name for resource naming | `string` | n/a | yes |
| environment | Environment name (dev/staging/prod) | `string` | n/a | yes |
| vpc_cidr | CIDR block for VPC | `string` | `"10.0.0.0/16"` | no |
| enable_nat_gateway | Enable NAT Gateways for private subnets | `bool` | `true` | no |
| single_nat_gateway | Use single NAT instead of one per AZ | `bool` | `false` | no |
| enable_flow_logs | Enable VPC Flow Logs | `bool` | `true` | no |
| flow_logs_retention_days | CloudWatch retention for flow logs | `number` | `7` | no |
| enable_s3_endpoint | Create S3 VPC endpoint (FREE) | `bool` | `true` | no |
| enable_dynamodb_endpoint | Create DynamoDB VPC endpoint (FREE) | `bool` | `false` | no |
| enable_ecr_endpoints | Create ECR VPC endpoints (~$22/mo) | `bool` | `false` | no |
| enable_ssm_endpoints | Create SSM VPC endpoints (~$22/mo) | `bool` | `true` | no |
| common_tags | Common tags for all resources | `map(string)` | `{}` | no |

See [variables.tf](./variables.tf) for complete list with descriptions and validation rules.

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| vpc_cidr | VPC CIDR block |
| public_subnet_ids | List of public subnet IDs |
| private_app_subnet_ids | List of private application subnet IDs |
| private_db_subnet_ids | List of private database subnet IDs |
| nat_gateway_public_ips | Public IPs of NAT Gateways (for whitelisting) |
| alb_security_group_id | Security group for ALB |
| web_tier_security_group_id | Security group for web/app instances |
| rds_security_group_id | Security group for RDS |

See [outputs.tf](./outputs.tf) for complete list.

## Architecture Diagram
```
Internet
    │
    ├─► Internet Gateway
    │       │
    │       ▼
    │   ┌────────────────────────────────────┐
    │   │  Public Subnets (3 AZs)            │
    │   │  - Application Load Balancer       │
    │   │  - NAT Gateways (3x)               │
    │   │  - Bastion (optional)              │
    │   └────────────────────────────────────┘
    │               │
    │               ▼
    │   ┌────────────────────────────────────┐
    │   │  Private App Subnets (3 AZs)       │
    │   │  - EC2 Auto Scaling Groups         │
    │   │  - ECS Tasks                       │
    │   │  - Lambda Functions                │
    │   └────────────────────────────────────┘
    │               │
    │               ▼
    │   ┌────────────────────────────────────┐
    │   │  Private DB Subnets (3 AZs)        │
    │   │  - RDS Multi-AZ                    │
    │   │  - ElastiCache                     │
    │   │  - No Internet Access              │
    │   └────────────────────────────────────┘
    │
    └─► VPC Endpoints
        - S3 (Gateway, FREE)
        - DynamoDB (Gateway, FREE)
        - ECR (Interface)
        - SSM (Interface)
```

## Cost Estimation

### Development Environment (Cost-Optimized)
- **VPC, Subnets, IGW**: FREE
- **Single NAT Gateway**: ~$32/month + $0.045/GB
- **S3 VPC Endpoint**: FREE
- **SSM VPC Endpoints** (3): ~$22/month
- **Flow Logs** (disabled): $0
- **Total**: ~$54/month + data transfer

### Production Environment (High Availability)
- **VPC, Subnets, IGW**: FREE
- **NAT Gateways** (3 AZs): ~$96/month + $0.045/GB
- **S3 & DynamoDB Endpoints**: FREE
- **SSM Endpoints** (3): ~$22/month
- **ECR Endpoints** (2): ~$22/month
- **Flow Logs**: ~$0.50/GB ingested
- **Total**: ~$140/month + data transfer + flow logs

### Cost Optimization Tips
1. **Use single NAT Gateway** for dev/staging ($66/month savings)
2. **Disable flow logs** in non-production ($10-50/month savings depending on traffic)
3. **Use S3 for flow logs** instead of CloudWatch (95% cheaper)
4. **Disable ECR endpoints** if not using containers ($22/month savings)
5. **Schedule NAT Gateway** deletion outside business hours for dev (advanced, requires automation)

## Security Best Practices

### Network Segmentation
- ✅ Public subnets: Only load balancers and NAT gateways
- ✅ Private app subnets: Application servers with NAT internet access
- ✅ Private DB subnets: Completely isolated, no internet access
- ✅ Separate route tables per tier for security boundaries

### Security Groups
- ✅ Least privilege: Only allow necessary ports
- ✅ Source restriction: Use security group IDs, not 0.0.0.0/0
- ✅ No SSH to instances: Use SSM Session Manager instead
- ✅ Database access: Only from application security group

### Monitoring
- ✅ VPC Flow Logs: Detect unusual traffic patterns
- ✅ CloudWatch Alarms: NAT Gateway bandwidth, VPC endpoint errors
- ✅ AWS Config Rules: Enforce security group best practices

### Access Control
- ✅ SSM Session Manager: No SSH keys, full audit trail
- ✅ IAM Policies: Least privilege for VPC modifications
- ✅ VPC Endpoints: Private AWS service access
