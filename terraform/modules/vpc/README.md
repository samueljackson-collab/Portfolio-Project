# VPC Module

Creates a production-ready VPC with public/private subnets, routing, optional NAT Gateway, and VPC Flow Logs.

## Inputs
- `name_prefix` (string): Prefix for resource names.
- `cidr_block` (string): VPC CIDR.
- `public_subnet_cidrs` (list(string)): Public subnet CIDRs.
- `private_subnet_cidrs` (list(string)): Private subnet CIDRs.
- `availability_zones` (list(string)): AZs to spread subnets across.
- `enable_nat_gateway` (bool): Create a shared NAT Gateway for private subnets.
- `enable_flow_logs` (bool): Enable VPC Flow Logs to CloudWatch.
- `tags` (map(string)): Common tags.

## Outputs
- `vpc_id`: VPC ID.
- `public_subnet_ids`: Public subnet IDs.
- `private_subnet_ids`: Private subnet IDs.
- `nat_gateway_id`: NAT Gateway ID when provisioned.
- `flow_log_group_name`: Flow log group name when enabled.
