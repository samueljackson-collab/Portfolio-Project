# Networking Module

## Overview

This module creates a production-ready VPC with multi-AZ public, private, and database subnets. It includes NAT gateways for private subnet egress, VPC Flow Logs for network monitoring, and VPC endpoints for AWS services.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                    VPC                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Public Subnets (3 AZs)                          ││
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                ││
│  │    │   us-west-2a │  │   us-west-2b │  │   us-west-2c │                ││
│  │    │   10.0.1.0/24│  │   10.0.2.0/24│  │   10.0.3.0/24│                ││
│  │    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                ││
│  │           │                 │                 │                         ││
│  │           ▼                 ▼                 ▼                         ││
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                ││
│  │    │ NAT Gateway  │  │ NAT Gateway  │  │ NAT Gateway  │ (prod)         ││
│  │    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                ││
│  │           │                 │                 │                         ││
│  └───────────┼─────────────────┼─────────────────┼─────────────────────────┘│
│              │                 │                 │                          │
│  ┌───────────┼─────────────────┼─────────────────┼─────────────────────────┐│
│  │           ▼                 ▼                 ▼                         ││
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                ││
│  │    │  Private     │  │  Private     │  │  Private     │                ││
│  │    │  10.0.11.0/24│  │  10.0.12.0/24│  │  10.0.13.0/24│                ││
│  │    └──────────────┘  └──────────────┘  └──────────────┘                ││
│  │                        Private Subnets                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                ││
│  │    │  Database    │  │  Database    │  │  Database    │                ││
│  │    │  10.0.21.0/24│  │  10.0.22.0/24│  │  10.0.23.0/24│                ││
│  │    └──────────────┘  └──────────────┘  └──────────────┘                ││
│  │                       Database Subnets (isolated)                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │            Internet Gateway              VPC Endpoints                  ││
│  │                 │                    (S3, DynamoDB)                     ││
│  └─────────────────┼───────────────────────────────────────────────────────┘│
│                    │                                                        │
└────────────────────┼────────────────────────────────────────────────────────┘
                     │
                     ▼
                 Internet
```

## Features

- **Multi-AZ Deployment**: Subnets distributed across 3 availability zones
- **Subnet Tiers**: Public, private, and database subnets
- **NAT Gateways**: Single or per-AZ NAT gateways for private subnet internet access
- **VPC Flow Logs**: Network traffic logging to CloudWatch
- **VPC Endpoints**: Gateway endpoints for S3 and DynamoDB
- **Kubernetes Ready**: Subnets tagged for EKS/ELB integration

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `name_prefix` | Prefix for resource names | `string` | - | Yes |
| `region` | AWS region for VPC endpoints | `string` | `"us-west-2"` | No |
| `vpc_cidr` | CIDR block for the VPC | `string` | `"10.0.0.0/16"` | No |
| `availability_zones` | List of availability zones | `list(string)` | `["us-west-2a", "us-west-2b", "us-west-2c"]` | No |
| `public_subnet_cidrs` | CIDR blocks for public subnets | `list(string)` | `["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]` | No |
| `private_subnet_cidrs` | CIDR blocks for private subnets | `list(string)` | `["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]` | No |
| `database_subnet_cidrs` | CIDR blocks for database subnets | `list(string)` | `["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]` | No |
| `enable_nat_gateway` | Enable NAT gateway for private subnets | `bool` | `true` | No |
| `single_nat_gateway` | Use single NAT gateway (cost savings) | `bool` | `false` | No |
| `enable_flow_logs` | Enable VPC Flow Logs | `bool` | `true` | No |
| `flow_logs_retention_days` | Flow logs retention in days | `number` | `30` | No |
| `enable_vpc_endpoints` | Create S3 and DynamoDB endpoints | `bool` | `true` | No |
| `create_custom_nacls` | Create custom Network ACLs | `bool` | `false` | No |
| `tags` | Tags to apply to all resources | `map(string)` | `{}` | No |

## Outputs

| Name | Description |
|------|-------------|
| `vpc_id` | The ID of the VPC |
| `vpc_cidr_block` | The CIDR block of the VPC |
| `vpc_arn` | The ARN of the VPC |
| `public_subnet_ids` | List of public subnet IDs |
| `private_subnet_ids` | List of private subnet IDs |
| `database_subnet_ids` | List of database subnet IDs |
| `database_subnet_group_name` | Name of the database subnet group |
| `internet_gateway_id` | The ID of the Internet Gateway |
| `nat_gateway_ids` | List of NAT Gateway IDs |
| `nat_gateway_public_ips` | List of NAT Gateway public IPs |
| `public_route_table_id` | The ID of the public route table |
| `private_route_table_ids` | List of private route table IDs |
| `s3_endpoint_id` | The ID of the S3 VPC endpoint |
| `flow_log_id` | The ID of the VPC Flow Log |

## Example Usage

### Basic VPC (Development)

```hcl
module "networking" {
  source = "./modules/networking"

  name_prefix        = "myapp-dev"
  vpc_cidr           = "10.0.0.0/16"
  single_nat_gateway = true  # Cost savings for dev

  tags = {
    Environment = "dev"
    Project     = "myapp"
  }
}
```

### Production VPC (High Availability)

```hcl
module "networking" {
  source = "./modules/networking"

  name_prefix         = "myapp-prod"
  vpc_cidr            = "10.0.0.0/16"
  single_nat_gateway  = false  # NAT per AZ for HA
  enable_flow_logs    = true
  enable_vpc_endpoints = true

  tags = {
    Environment = "production"
    Project     = "myapp"
  }
}
```

### Custom CIDR Blocks

```hcl
module "networking" {
  source = "./modules/networking"

  name_prefix           = "myapp-staging"
  vpc_cidr              = "172.16.0.0/16"
  availability_zones    = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs   = ["172.16.1.0/24", "172.16.2.0/24"]
  private_subnet_cidrs  = ["172.16.11.0/24", "172.16.12.0/24"]
  database_subnet_cidrs = ["172.16.21.0/24", "172.16.22.0/24"]

  tags = {
    Environment = "staging"
  }
}
```

## Important Notes

1. **NAT Gateway Costs**: NAT Gateways incur hourly charges plus data processing fees. Use `single_nat_gateway = true` for non-production environments.

2. **VPC Flow Logs**: Enable for security auditing and troubleshooting. Logs are stored in CloudWatch and incur storage costs.

3. **Database Subnets**: Isolated from the internet by default. Use VPC endpoints for AWS service access.

4. **Kubernetes Integration**: Subnets are automatically tagged for EKS cluster integration.

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.4 |
| aws | ~> 5.0 |
