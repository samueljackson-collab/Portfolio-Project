# Compute Module

## Overview

This module creates compute resources including Auto Scaling Groups, Launch Templates, Application Load Balancers, and associated target groups for hosting web applications.

## Architecture

```
                              Internet
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Application Load      │
                    │  Balancer (Public)     │
                    │  ┌──────────────────┐  │
                    │  │ HTTP (80) → 443  │  │
                    │  │ HTTPS (443)      │  │
                    │  └──────────────────┘  │
                    └────────────┬───────────┘
                                 │
                    ┌────────────┴───────────┐
                    ▼                        ▼
          ┌─────────────────┐      ┌─────────────────┐
          │  Target Group   │      │  Health Checks  │
          │  (/healthz)     │      │  (30s interval) │
          └────────┬────────┘      └─────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ EC2     │  │ EC2     │  │ EC2     │
│ (AZ-a)  │  │ (AZ-b)  │  │ (AZ-c)  │
└─────────┘  └─────────┘  └─────────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
          Auto Scaling Group
          (min: 2, max: 6)
```

## Features

- **Auto Scaling**: Dynamic scaling based on CPU utilization and request count
- **Launch Templates**: IMDSv2 required, SSM access enabled, CloudWatch agent
- **Application Load Balancer**: HTTP to HTTPS redirect, health checks
- **Security Groups**: Least privilege access between ALB and instances
- **Instance Refresh**: Rolling deployments with configurable health threshold

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `name_prefix` | Prefix for resource names | `string` | - | Yes |
| `vpc_id` | ID of the VPC | `string` | - | Yes |
| `public_subnet_ids` | List of public subnet IDs for ALB | `list(string)` | - | Yes |
| `private_subnet_ids` | List of private subnet IDs for ASG | `list(string)` | - | Yes |
| `instance_type` | EC2 instance type | `string` | `"t3.small"` | No |
| `ami_ssm_parameter` | SSM parameter for AMI ID | `string` | `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64` | No |
| `app_port` | Application port | `number` | `80` | No |
| `user_data` | Custom user data script | `string` | `""` | No |
| `min_size` | Minimum ASG size | `number` | `2` | No |
| `max_size` | Maximum ASG size | `number` | `6` | No |
| `desired_capacity` | Desired ASG capacity | `number` | `2` | No |
| `health_check_path` | ALB health check path | `string` | `"/healthz"` | No |
| `target_cpu_utilization` | Target CPU for scaling | `number` | `70` | No |
| `acm_certificate_arn` | ACM certificate ARN for HTTPS | `string` | `""` | No |
| `enable_deletion_protection` | ALB deletion protection | `bool` | `false` | No |
| `allowed_cidr_blocks` | CIDRs allowed to access ALB | `list(string)` | `["0.0.0.0/0"]` | No |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | No |

## Outputs

| Name | Description |
|------|-------------|
| `alb_id` | The ID of the ALB |
| `alb_arn` | The ARN of the ALB |
| `alb_dns_name` | The DNS name of the ALB |
| `alb_zone_id` | The zone ID for Route53 alias |
| `target_group_arn` | The ARN of the target group |
| `asg_id` | The ID of the Auto Scaling Group |
| `asg_name` | The name of the ASG |
| `launch_template_id` | The ID of the launch template |
| `alb_security_group_id` | The ID of the ALB security group |
| `app_security_group_id` | The ID of the app security group |
| `instance_role_arn` | The ARN of the instance IAM role |

## Example Usage

### Basic Web Tier

```hcl
module "compute" {
  source = "./modules/compute"

  name_prefix        = "myapp-dev"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  instance_type    = "t3.small"
  min_size         = 2
  max_size         = 4
  desired_capacity = 2

  tags = {
    Environment = "dev"
    Project     = "myapp"
  }
}
```

### Production with HTTPS

```hcl
module "compute" {
  source = "./modules/compute"

  name_prefix        = "myapp-prod"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  instance_type            = "t3.medium"
  min_size                 = 3
  max_size                 = 10
  desired_capacity         = 3
  acm_certificate_arn      = "arn:aws:acm:us-west-2:123456789012:certificate/abc123"
  enable_deletion_protection = true

  target_cpu_utilization       = 60
  enable_request_based_scaling = true
  target_requests_per_instance = 500

  tags = {
    Environment = "production"
  }
}
```

### Custom User Data

```hcl
module "compute" {
  source = "./modules/compute"

  name_prefix        = "myapp-custom"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  user_data = <<-EOF
    #!/bin/bash
    dnf update -y
    dnf install -y docker
    systemctl enable docker --now
    docker run -d -p 80:8080 myapp:latest
  EOF

  app_port         = 80
  health_check_path = "/api/health"

  tags = {
    Environment = "custom"
  }
}
```

## Important Notes

1. **IMDSv2**: Launch template enforces IMDSv2 for enhanced security. All metadata requests must use tokens.

2. **SSM Access**: Instances have SSM managed instance core policy attached. Use Session Manager instead of SSH.

3. **Health Checks**: Configure `health_check_path` to match your application's health endpoint.

4. **Instance Refresh**: Deployments use rolling updates with 50% minimum healthy percentage.

5. **SSL/TLS**: Without an ACM certificate, the ALB only serves HTTP. Add `acm_certificate_arn` for HTTPS.

## Security Considerations

- ALB security group allows inbound 80/443 from `allowed_cidr_blocks`
- App security group only allows traffic from ALB security group
- Instances are in private subnets with no public IP
- CloudWatch agent policy enables metrics and logs collection

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.4 |
| aws | ~> 5.0 |
