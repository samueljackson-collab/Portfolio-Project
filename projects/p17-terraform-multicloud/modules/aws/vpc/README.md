# AWS VPC Module

Creates a multi-AZ VPC with public/private subnets, NAT gateways, VPC endpoints, and flow logs.

## Usage

```hcl
module "vpc" {
  source = "../modules/aws/vpc"

  project_name          = "portfolio"
  environment           = "dev"
  region                = "us-east-1"
  vpc_cidr              = "10.20.0.0/16"
  azs                   = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs   = ["10.20.10.0/24", "10.20.11.0/24"]
  private_subnet_cidrs  = ["10.20.20.0/24", "10.20.21.0/24"]
  enable_nat_gateway    = true
  enable_flow_logs      = true
  interface_endpoints   = ["ssm", "ec2messages"]
  gateway_endpoints     = ["s3", "dynamodb"]
  tags = {
    Owner = "platform-team"
  }
}
```

## Outputs
- `vpc_id`
- `public_subnet_ids`
- `private_subnet_ids`
- `nat_gateway_ids`
- `vpc_endpoint_ids`
- `flow_log_id`
