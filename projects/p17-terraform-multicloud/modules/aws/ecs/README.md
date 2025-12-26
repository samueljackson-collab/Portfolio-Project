# AWS ECS Module

Deploys an ECS Fargate cluster, task definition, service, optional load balancer wiring, autoscaling, and CloudWatch logging.

## Usage

```hcl
module "ecs" {
  source = "../modules/aws/ecs"

  project_name     = "portfolio"
  environment      = "prod"
  region           = "us-east-1"
  vpc_id           = module.vpc.vpc_id
  subnet_ids       = module.vpc.private_subnet_ids
  container_image  = "nginx:latest"
  container_port   = 8080
  desired_count    = 2
  enable_autoscaling = true
}
```

## Outputs
- `cluster_id`
- `service_name`
- `task_definition_arn`
- `security_group_id`
