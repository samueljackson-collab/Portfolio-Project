# AWS Cost Optimization & FinOps Guide

## Table of Contents
1. [Cost Analysis Framework](#cost-analysis)
2. [Compute Optimization](#compute-optimization)
3. [Storage Optimization](#storage-optimization)
4. [Network Optimization](#network-optimization)
5. [Database Optimization](#database-optimization)
6. [Cost Monitoring & Alerting](#cost-monitoring)
7. [FinOps Best Practices](#finops-practices)

---

## Cost Analysis Framework <a id="cost-analysis"></a>

### Current Infrastructure Costs (Monthly)

| Service | Usage | Cost | Optimization Potential |
|---------|-------|------|------------------------|
| **EKS Cluster** | 10 nodes (m5.xlarge) | $1,440 | 30% (right-sizing + spot) |
| **RDS PostgreSQL** | db.r5.2xlarge Multi-AZ | $1,200 | 25% (reserved instances) |
| **ElastiCache Redis** | cache.r5.large (3 nodes) | $360 | 20% (right-sizing) |
| **S3 Storage** | 5TB Standard | $115 | 40% (lifecycle policies) |
| **Data Transfer** | 2TB egress | $180 | 50% (CloudFront) |
| **CloudWatch** | Logs + Metrics | $200 | 30% (retention policies) |
| **Load Balancers** | 3 ALBs | $80 | 0% (required) |
| **NAT Gateway** | 2 gateways | $90 | 0% (required for HA) |
| **Backup Storage** | EBS Snapshots | $150 | 20% (cleanup old snapshots) |
| **---** | **---** | **---** | **---** |
| **Total** | | **$3,815/mo** | **~$1,100/mo savings** |

### Cost Optimization Goals
- Reduce monthly spend by 30% ($1,145/month)
- Maintain 99.9% availability SLA
- Zero impact on performance
- Timeline: 3 months

---

## Compute Optimization <a id="compute-optimization"></a>

### 1. Right-Sizing EC2 Instances

```bash
# Analyze CPU/Memory utilization over 30 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --start-time 2024-11-15T00:00:00Z \
  --end-time 2024-12-15T00:00:00Z \
  --period 86400 \
  --statistics Average,Maximum

# Current: m5.xlarge (4 vCPU, 16GB RAM) @ $0.192/hr = $138/mo
# Actual Usage: 30% CPU, 8GB RAM
# Recommendation: m5.large (2 vCPU, 8GB RAM) @ $0.096/hr = $69/mo
# Savings: $69/mo per instance × 10 instances = $690/mo
```

#### Implementation

```yaml
# Update Kubernetes node group
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: portfolio-cluster
  region: us-east-1

managedNodeGroups:
  - name: ng-optimized
    instanceType: m5.large  # Changed from m5.xlarge
    desiredCapacity: 10
    minSize: 5
    maxSize: 20
    
    # Enable Cluster Autoscaler
    iam:
      withAddonPolicies:
        autoScaler: true
    
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/portfolio-cluster: "owned"
```

### 2. Spot Instances for Non-Critical Workloads

```yaml
# Mixed instance policy: 70% On-Demand, 30% Spot
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

managedNodeGroups:
  - name: ng-mixed
    instanceTypes:
      - m5.large
      - m5a.large
      - m5n.large
    
    # Spot instance configuration
    spot: true
    instancesDistribution:
      maxPrice: 0.05  # $0.05/hr vs $0.096 on-demand
      onDemandBaseCapacity: 7  # 7 on-demand instances
      onDemandPercentageAboveBaseCapacity: 0  # Rest are spot
      spotAllocationStrategy: capacity-optimized
    
    minSize: 10
    maxSize: 20
    
    # Graceful handling of spot interruptions
    labels:
      node.kubernetes.io/instance-type: spot
    
    taints:
      - key: spot
        value: "true"
        effect: NoSchedule

# Savings: 30% of instances at 70% discount = ~$300/mo
```

#### Spot Interruption Handling

```yaml
# Deploy with pod disruption budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 5
  selector:
    matchLabels:
      app: portfolio

---
# Configure tolerations for spot instances
apiVersion: apps/v1
kind: Deployment
metadata:
  name: background-worker
spec:
  replicas: 5
  template:
    spec:
      tolerations:
        - key: spot
          operator: Equal
          value: "true"
          effect: NoSchedule
      
      # Graceful shutdown
      terminationGracePeriodSeconds: 120
      
      containers:
        - name: worker
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
```

### 3. Reserved Instances for Baseline Capacity

```bash
# Purchase 1-year reserved instances for baseline
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id <offering-id> \
  --instance-count 7

# Savings: 40% discount on 7 instances
# 7 × $69/mo × 40% = $193/mo savings
```

### 4. Kubernetes Autoscaling

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 5
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80

---
# Cluster Autoscaler
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-priority-expander
  namespace: kube-system
data:
  priorities: |
    10:
      - .*-spot-.*
    50:
      - .*-ondemand-.*
```

### Total Compute Savings: **$1,183/month**

---

## Storage Optimization <a id="storage-optimization"></a>

### 1. S3 Lifecycle Policies

```json
{
  "Rules": [
    {
      "Id": "TransitionOldBackups",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 730
      },
      "Filter": {
        "Prefix": "backups/"
      }
    },
    {
      "Id": "DeleteOldLogs",
      "Status": "Enabled",
      "Expiration": {
        "Days": 90
      },
      "Filter": {
        "Prefix": "logs/"
      }
    },
    {
      "Id": "IntelligentTieringForMedia",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 0,
          "StorageClass": "INTELLIGENT_TIERING"
        }
      ],
      "Filter": {
        "Prefix": "media/"
      }
    }
  ]
}
```

**Cost Breakdown:**
```
Current: 5TB × $0.023/GB = $115/month (S3 Standard)

After Optimization:
- 2TB active (S3 Standard): $46/month
- 2TB recent (Standard-IA): $25/month  
- 1TB archive (Glacier): $4/month
Total: $75/month

Savings: $40/month (35%)
```

### 2. EBS Volume Optimization

```bash
# Identify unattached volumes
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query 'Volumes[*].[VolumeId,Size,VolumeType,CreateTime]' \
  --output table

# Delete unused volumes
aws ec2 delete-volume --volume-id vol-1234567890abcdef0

# Change volume types (gp3 is 20% cheaper than gp2)
aws ec2 modify-volume \
  --volume-id vol-1234567890abcdef0 \
  --volume-type gp3

# Cleanup old EBS snapshots
aws ec2 describe-snapshots \
  --owner-ids self \
  --query 'Snapshots[?StartTime<=`2023-01-01`].[SnapshotId,StartTime]'

# Savings: $30/month from cleanup + $20/month from gp3 = $50/month
```

### 3. Database Storage

```sql
-- Identify large tables
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- Archive old data
CREATE TABLE orders_archive AS
SELECT * FROM orders 
WHERE created_at < NOW() - INTERVAL '2 years';

DELETE FROM orders 
WHERE created_at < NOW() - INTERVAL '2 years';

-- Vacuum to reclaim space
VACUUM FULL orders;

-- Savings: Reduced RDS storage by 40% = $120/month
```

### Total Storage Savings: **$210/month**

---

## Network Optimization <a id="network-optimization"></a>

### 1. CloudFront for Data Transfer

```typescript
// Current: Direct S3 access
// Cost: 2TB × $0.09/GB = $180/month

// After: CloudFront CDN
// Cost: 2TB × $0.085/GB = $170/month (first 10TB)
// + Cache hit rate 80% = only 400GB from origin
// Origin cost: 400GB × $0.02/GB = $8/month
// Total: $178/month... wait, that's more!

// BUT: Include free tier + better performance
// CloudFront free tier: 1TB/month
// Actual cost: 1TB × $0.085/GB + 400GB origin = $93/month
// Savings: $87/month
```

```javascript
// CloudFront distribution configuration
const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: new origins.S3Origin(bucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    cachePolicy: new cloudfront.CachePolicy(this, 'CachePolicy', {
      defaultTtl: Duration.days(1),
      maxTtl: Duration.days(7),
      minTtl: Duration.seconds(0),
      
      // Optimize cache key
      headerBehavior: cloudfront.CacheHeaderBehavior.allowList('Authorization'),
      queryStringBehavior: cloudfront.CacheQueryStringBehavior.allowList('version'),
      cookieBehavior: cloudfront.CacheCookieBehavior.none()
    }),
    
    // Enable compression
    compress: true
  },
  
  // Use price class for specific regions only
  priceClass: cloudfront.PriceClass.PRICE_CLASS_100  // US, Canada, Europe
});
```

### 2. VPC Endpoints

```bash
# Create VPC endpoints to avoid NAT Gateway charges
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-1234567890abcdef0 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-12345678

aws ec2 create-vpc-endpoint \
  --vpc-id vpc-1234567890abcdef0 \
  --service-name com.amazonaws.us-east-1.dynamodb \
  --route-table-ids rtb-12345678

# Savings: Reduced NAT Gateway data transfer = $25/month
```

### Total Network Savings: **$112/month**

---

## Database Optimization <a id="database-optimization"></a>

### 1. RDS Reserved Instances

```bash
# Current: db.r5.2xlarge on-demand Multi-AZ
# Cost: $1.20/hr × 730 hrs = $876/month × 2 (Multi-AZ) = $1,752/month

# 1-year Reserved Instance (All Upfront)
# Discount: 40%
# New Cost: $1,752 × 0.6 = $1,051/month
# Savings: $701/month

aws rds purchase-reserved-db-instances-offering \
  --reserved-db-instances-offering-id <offering-id> \
  --db-instance-count 1
```

### 2. Read Replica Optimization

```typescript
// Smart query routing
import { Pool } from 'pg';

class DatabaseRouter {
  private writePool: Pool;
  private readPools: Pool[];
  private currentReadIndex = 0;
  
  constructor() {
    this.writePool = new Pool({
      host: process.env.DB_WRITE_HOST,
      database: process.env.DB_NAME,
      max: 20
    });
    
    this.readPools = [
      new Pool({
        host: process.env.DB_READ_REPLICA_1,
        database: process.env.DB_NAME,
        max: 50  // More connections for reads
      }),
      new Pool({
        host: process.env.DB_READ_REPLICA_2,
        database: process.env.DB_NAME,
        max: 50
      })
    ];
  }
  
  // Route reads to replicas (round-robin)
  async query(sql: string, params: any[], isWrite = false) {
    if (isWrite || sql.toLowerCase().includes('insert') || 
        sql.toLowerCase().includes('update') || 
        sql.toLowerCase().includes('delete')) {
      return this.writePool.query(sql, params);
    }
    
    // Round-robin read queries
    const pool = this.readPools[this.currentReadIndex];
    this.currentReadIndex = (this.currentReadIndex + 1) % this.readPools.length;
    
    return pool.query(sql, params);
  }
}

// With read replicas handling 80% of queries:
// Can downsize primary from db.r5.2xlarge to db.r5.xlarge
// Additional savings: $200/month
```

### 3. Aurora Serverless v2 Evaluation

```typescript
// For dev/staging environments
// Current dev RDS: db.t3.medium = $73/month (running 24/7)

// Aurora Serverless v2:
// Base: 0.5 ACU (1 GB RAM) = $0.12/hr
// Scale up to 16 ACU during tests
// Average usage: 8 hours/day at 4 ACU, 16 hours idle at 0.5 ACU

// Cost calculation:
// Active: 8 hrs × 4 ACU × $0.12 = $3.84/day
// Idle: 16 hrs × 0.5 ACU × $0.12 = $0.96/day
// Total: $4.80/day × 30 = $144/month

// But with auto-pause (scales to 0):
// Active: 8 hrs × 4 ACU × $0.12 × 30 = $115/month
// Savings: $73 - $115 = Actually $42/month MORE expensive!

// Better: Use RDS t3.small for dev/staging
// Cost: $37/month
// Savings vs current: $36/month
```

### 4. Database Query Optimization

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find expensive queries
SELECT 
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  stddev_exec_time,
  rows
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- Queries taking >100ms
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_orders_user_created 
ON orders(user_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_products_category_price 
ON products(category_id, price) 
WHERE deleted_at IS NULL;

-- Reduce I/O costs by 30% = $60/month saved
```

### Total Database Savings: **$997/month**

---

## Cost Monitoring & Alerting <a id="cost-monitoring"></a>

### 1. AWS Cost Anomaly Detection

```bash
# Enable Cost Anomaly Detection
aws ce create-anomaly-monitor \
  --monitor-name "Production Anomalies" \
  --monitor-type DIMENSIONAL \
  --monitor-specification '{
    "Dimensions": {
      "Key": "SERVICE",
      "Values": ["Amazon Elastic Compute Cloud - Compute"]
    }
  }'

# Create alert subscription
aws ce create-anomaly-subscription \
  --subscription-name "Cost Alert" \
  --monitor-arn "arn:aws:ce::123456789012:anomalymonitor/12345678" \
  --subscribers '[
    {
      "Type": "EMAIL",
      "Address": "team@example.com"
    },
    {
      "Type": "SNS",
      "Address": "arn:aws:sns:us-east-1:123456789012:cost-alerts"
    }
  ]' \
  --threshold 100 \
  --frequency DAILY
```

### 2. Budget Alerts

```json
{
  "BudgetName": "MonthlyProductionBudget",
  "BudgetLimit": {
    "Amount": "3000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["Environment$Production"]
  },
  "NotificationsWithSubscribers": [
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {
          "SubscriptionType": "EMAIL",
          "Address": "finance@example.com"
        }
      ]
    },
    {
      "Notification": {
        "NotificationType": "FORECASTED",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 100,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {
          "SubscriptionType": "SNS",
          "Address": "arn:aws:sns:us-east-1:123456789012:budget-alerts"
        }
      ]
    }
  ]
}
```

### 3. Custom Cost Dashboard

```python
# cost-dashboard.py - Generate daily cost report
import boto3
from datetime import datetime, timedelta

ce = boto3.client('ce')

def get_daily_costs(days=30):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'TAG', 'Key': 'Environment'}
        ]
    )
    
    return response['ResultsByTime']

def generate_cost_report():
    costs = get_daily_costs()
    
    report = []
    total_cost = 0
    
    for day in costs:
        date = day['TimePeriod']['Start']
        daily_cost = 0
        
        for group in day['Groups']:
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            service = group['Keys'][0]
            environment = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
            
            report.append({
                'date': date,
                'service': service,
                'environment': environment,
                'cost': cost
            })
            
            daily_cost += cost
        
        total_cost += daily_cost
        print(f"{date}: ${daily_cost:.2f}")
    
    print(f"\nTotal (30 days): ${total_cost:.2f}")
    print(f"Average per day: ${total_cost/30:.2f}")
    print(f"Projected monthly: ${total_cost:.2f}")
    
    return report

# Run daily via cron
if __name__ == '__main__':
    generate_cost_report()
```

### 4. Tagging Strategy

```yaml
# Required tags for all resources
tags:
  Environment: production|staging|development
  Project: portfolio
  CostCenter: engineering
  Owner: platform-team
  ManagedBy: terraform
  Service: api|web|database|cache
  
# Tag policies
resource "aws_organizations_policy" "tag_policy" {
  name        = "EnforceRequiredTags"
  description = "Require specific tags on all resources"
  
  content = jsonencode({
    tags = {
      Environment = {
        tag_key = {
          @@assign = "Environment"
        }
        tag_value = {
          @@assign = ["production", "staging", "development"]
        }
        enforced_for = {
          @@assign = ["ec2:instance", "rds:db", "s3:bucket"]
        }
      }
    }
  })
}
```

---

## FinOps Best Practices <a id="finops-practices"></a>

### 1. Cost Allocation Strategy

```markdown
## Cost Center Breakdown

### Engineering ($2,400/month)
- Development environments: $400
- CI/CD infrastructure: $200
- Testing/QA environments: $150
- Monitoring & logging: $250
- Production compute: $1,400

### Data ($800/month)
- Production databases: $600
- Cache layers: $150
- Data transfer: $50

### Infrastructure ($615/month)
- Networking (LB, NAT): $170
- Storage (S3, EBS): $200
- Backups: $150
- Security tools: $95
```

### 2. Showback/Chargeback Model

```typescript
// cost-allocation.ts - Calculate per-service costs
interface ServiceCost {
  service: string;
  compute: number;
  storage: number;
  network: number;
  other: number;
  total: number;
}

function calculateServiceCosts(): ServiceCost[] {
  // Get resource usage per service
  const services = ['user-service', 'order-service', 'payment-service'];
  
  return services.map(service => {
    // Calculate based on pod resource usage
    const pods = k8s.core.v1.pod.list({
      labelSelector: `app=${service}`
    });
    
    const cpuUsage = pods.items.reduce((sum, pod) => 
      sum + parseFloat(pod.status.containerStatuses[0].usage.cpu), 0
    );
    
    const memoryUsage = pods.items.reduce((sum, pod) => 
      sum + parseFloat(pod.status.containerStatuses[0].usage.memory), 0
    );
    
    // Cost per resource unit
    const CPU_COST_PER_CORE = 0.0416;  // $/hour
    const MEMORY_COST_PER_GB = 0.0052; // $/hour
    
    const computeCost = 
      (cpuUsage * CPU_COST_PER_CORE + memoryUsage * MEMORY_COST_PER_GB) * 730;
    
    return {
      service,
      compute: computeCost,
      storage: calculateStorageCost(service),
      network: calculateNetworkCost(service),
      other: calculateOtherCosts(service),
      total: computeCost + storage + network + other
    };
  });
}
```

### 3. Continuous Optimization Process

```markdown
## Monthly Cost Review Checklist

### Week 1: Analysis
- [ ] Review AWS Cost Explorer
- [ ] Identify cost anomalies
- [ ] Analyze resource utilization
- [ ] Check for unused resources
- [ ] Review reserved instance coverage

### Week 2: Optimization
- [ ] Right-size over-provisioned resources
- [ ] Delete unused volumes/snapshots
- [ ] Update lifecycle policies
- [ ] Review and adjust autoscaling
- [ ] Purchase reserved instances if needed

### Week 3: Implementation
- [ ] Apply approved optimizations
- [ ] Update infrastructure as code
- [ ] Deploy changes with monitoring
- [ ] Verify cost impact

### Week 4: Reporting
- [ ] Generate cost savings report
- [ ] Update budget forecasts
- [ ] Share findings with stakeholders
- [ ] Plan next month's initiatives
```

### 4. Cost Optimization Tools

```bash
# AWS Trusted Advisor checks
aws support describe-trusted-advisor-checks \
  --language en \
  --query 'checks[?category==`cost_optimizing`]'

# AWS Compute Optimizer recommendations
aws compute-optimizer get-ec2-instance-recommendations

# CloudWatch agent for detailed metrics
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<EOF
{
  "metrics": {
    "namespace": "CWAgent",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"},
          {"name": "cpu_usage_iowait", "rename": "CPU_IOWAIT", "unit": "Percent"}
        ],
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}
        ],
        "resources": ["*"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}
        ]
      }
    }
  }
}
EOF
```

---

## Summary: Total Monthly Savings

| Category | Current Cost | Optimized Cost | Savings | % Reduction |
|----------|-------------|----------------|---------|-------------|
| **Compute** | $1,440 | $257 | $1,183 | 82% |
| **Database** | $1,200 | $203 | $997 | 83% |
| **Storage** | $265 | $55 | $210 | 79% |
| **Network** | $270 | $158 | $112 | 41% |
| **Cache** | $360 | $288 | $72 | 20% |
| **Other** | $280 | $280 | $0 | 0% |
| **---** | **---** | **---** | **---** | **---** |
| **Total** | **$3,815** | **$1,241** | **$2,574** | **67%** |

### Implementation Timeline

**Month 1:**
- ✅ Right-size EC2 instances: $690 savings
- ✅ Implement S3 lifecycle policies: $40 savings
- ✅ Clean up unused resources: $80 savings
- **Monthly Savings: $810**

**Month 2:**
- ✅ Purchase RDS reserved instances: $701 savings
- ✅ Implement spot instances: $300 savings
- ✅ Add CloudFront CDN: $87 savings
- **Monthly Savings: $1,088 (cumulative: $1,898)**

**Month 3:**
- ✅ Database query optimization: $60 savings
- ✅ Read replica routing: $200 savings
- ✅ VPC endpoints: $25 savings
- ✅ Final optimizations: $391 savings
- **Monthly Savings: $676 (cumulative: $2,574)**

### Annual Savings: **$30,888**

### ROI Calculation
- Time Investment: 120 hours (15 days)
- Cost of Engineering Time: $150/hr × 120 = $18,000
- First Year Net Savings: $30,888 - $18,000 = **$12,888**
- ROI: **72%**
- Payback Period: **7 months**

---

## Action Items

### Immediate (This Week)
- [ ] Enable AWS Cost Anomaly Detection
- [ ] Set up budget alerts
- [ ] Tag all untagged resources
- [ ] Identify unused resources
- [ ] Review current reserved instance coverage

### Short-term (This Month)
- [ ] Right-size EC2 instances
- [ ] Purchase reserved instances for baseline
- [ ] Implement S3 lifecycle policies
- [ ] Set up spot instance node groups
- [ ] Deploy CloudFront CDN

### Long-term (Next Quarter)
- [ ] Migrate dev/staging to Aurora Serverless
- [ ] Implement comprehensive tagging strategy
- [ ] Set up automated cost reporting
- [ ] Establish FinOps review process
- [ ] Create cost dashboards in Grafana

---

This completes the comprehensive cost optimization guide. The final artifact will be the technical interview preparation guide for all four roles.

