# Networking Module

## Purpose
Provisions a production-ready AWS VPC with three-tier network architecture, implementing security best practices and high availability design patterns.

## Architecture

### Network Tiers
1. **Public Subnets**: Internet-facing resources (ALB, NAT Gateway, Bastion)
2. **Private App Subnets**: Application servers (EC2, ECS, Lambda)
3. **Private DB Subnets**: Database layer (RDS, ElastiCache)

### High Availability
- Multi-AZ deployment (2-3 availability zones)
- NAT Gateway per AZ (optional single NAT for cost savings)
- Subnet per AZ per tier (9 total subnets for 3-AZ deployment)

### Security Features
- Network ACLs at subnet level (stateless firewall)
- Private subnets with no direct internet access
- Database subnets completely isolated (no NAT Gateway)
- VPC Flow Logs for traffic monitoring and security auditing
- VPC Endpoints for private AWS service access (S3, DynamoDB)

### Cost Optimization
- Configurable NAT Gateway deployment (single vs per-AZ)
- Gateway endpoints for S3/DynamoDB (free, reduces data transfer)
- Configurable VPC Flow Logs retention

## Usage

### Basic Example
```hcl
module "networking" {
  source = "../modules/networking"

  project_name       = "my-app"
  environment        = "prod"
  aws_region         = "us-west-2"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  vpc_cidr = "10.0.0.0/16"

  enable_nat_gateway   = true
  single_nat_gateway   = false
  enable_vpc_flow_logs = true
  enable_s3_endpoint   = true

  common_tags = {
    Project   = "three-tier-app"
    ManagedBy = "Terraform"
    Owner     = "DevOps Team"
  }
}
```

### Cost-Optimized Dev Environment
```hcl
module "networking" {
  source = "../modules/networking"

  project_name       = "my-app"
  environment        = "dev"
  availability_zones = ["us-west-2a", "us-west-2b"]

  vpc_cidr = "10.1.0.0/16"

  enable_nat_gateway = true
  single_nat_gateway = true
  enable_vpc_flow_logs = false

  common_tags = {
    Project     = "three-tier-app"
    Environment = "dev"
  }
}
```

## Outputs
Refer to `outputs.tf` for all exported values. Key outputs include subnet IDs, route tables, NAT gateways, and flow log destinations.

## Subnet CIDR Calculations
For a `10.0.0.0/16` VPC with 3 AZs:

- Public: `10.0.0.0/24`, `10.0.1.0/24`, `10.0.2.0/24`
- Private App: `10.0.10.0/24`, `10.0.11.0/24`, `10.0.12.0/24`
- Private DB: `10.0.20.0/24`, `10.0.21.0/24`, `10.0.22.0/24`

## Security Considerations
- Public subnets host only ingress components (ALB, bastion)
- Application tier uses NAT gateways for egress
- Database tier is isolated with no internet path
- Flow logs provide audit trail for compliance frameworks (SOC 2, PCI)

## Monitoring & Troubleshooting
- Monitor NAT Gateway metrics (ActiveConnectionCount, BytesIn/Out)
- Alert on Flow Log delivery failures
- Use VPC Flow Logs to trace unusual traffic patterns

## References
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [NAT Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
