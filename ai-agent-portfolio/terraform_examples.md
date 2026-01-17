# Terraform Call Usage Examples

## Basic Module Instantiation
```hcl
module "web_app" {
  source = "github.com/your-org/terraform-aws-webapp"

  environment = "production"
  vpc_id      = "vpc-123456"

  # Auto-scaling configuration
  min_size     = 2
  max_size     = 10
  desired_size = 3

  # Feature flags
  enable_cdn        = true
  enable_monitoring = true
  enable_backups    = true
}
```

## Multi-Cloud Deployment
```hcl
module "multi_cloud_app" {
  source = "github.com/your-org/terraform-multi-cloud"

  providers = {
    aws   = aws.primary
    azure = azurerm.secondary
    gcp   = google.tertiary
  }

  regions = ["us-east-1", "eu-west-1", "asia-southeast1"]

  traffic_distribution = {
    primary   = 60
    secondary = 30
    tertiary  = 10
  }
}
```

## Kubernetes Cluster with AI-Optimized Config
```hcl
module "ai_ready_k8s" {
  source = "github.com/your-org/terraform-k8s-ai"

  cluster_name = "ml-platform"
  node_count   = 5

  gpu_enabled   = true
  ml_frameworks = ["pytorch", "tensorflow", "jupyter"]
  storage_class = "high-performance"

  auto_scaling = {
    enabled      = true
    min_replicas = 3
    max_replicas = 50
    metrics_type = "custom/ml-workload"
  }
}
```
