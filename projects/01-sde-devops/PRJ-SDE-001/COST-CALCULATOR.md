# AWS RDS Cost Calculator - Terraform Module

**Project:** PRJ-SDE-001 - Production Database Infrastructure
**Region:** us-west-2 (Oregon)
**Pricing:** As of January 2025
**Currency:** USD

---

## Quick Cost Reference

| Environment | Instance | Multi-AZ | Storage | Backups | Monthly Cost |
|-------------|----------|----------|---------|---------|--------------|
| **Development** | db.t3.micro | No | 20 GB | 1 day | **~$15** |
| **Staging** | db.t3.small | No | 20 GB | 7 days | **~$40** |
| **Production (Basic)** | db.t3.medium | No | 100 GB | 30 days | **~$150** |
| **Production (HA)** | db.r6g.large | Yes | 100 GB | 30 days | **~$310** |
| **Production (Premium)** | db.r6g.xlarge | Yes | 500 GB | 30 days | **~$700** |

---

## Detailed Cost Breakdown

### Development Environment

**Configuration:**
```hcl
instance_class = "db.t3.micro"
allocated_storage = 20
multi_az = false
backup_retention_period = 1
```

**Monthly Cost Breakdown:**
```
Component                          Qty    Rate/Unit    Monthly Cost
─────────────────────────────────────────────────────────────────────
RDS Instance (db.t3.micro)         730h   $0.017/hr    $12.41
RDS Storage (General Purpose SSD)  20GB   $0.115/GB    $2.30
Backup Storage (first 20GB free)   0GB    $0.095/GB    $0.00
Data Transfer Out                  1GB    $0.09/GB     $0.09
─────────────────────────────────────────────────────────────────────
TOTAL                                                  $14.80/month
                                                       $177.60/year
```

**Use Case:** Local development, feature testing, proof-of-concepts

---

### Staging Environment

**Configuration:**
```hcl
instance_class = "db.t3.small"
allocated_storage = 20
multi_az = false
backup_retention_period = 7
```

**Monthly Cost Breakdown:**
```
Component                          Qty    Rate/Unit    Monthly Cost
─────────────────────────────────────────────────────────────────────
RDS Instance (db.t3.small)         730h   $0.034/hr    $24.82
RDS Storage (GP SSD)               20GB   $0.115/GB    $2.30
Backup Storage (excess over 20GB)  10GB   $0.095/GB    $0.95
Data Transfer Out                  5GB    $0.09/GB     $0.45
CloudWatch Logs                    1GB    $0.50/GB     $0.50
─────────────────────────────────────────────────────────────────────
TOTAL                                                  $29.02/month
                                                       $348.24/year
```

**Use Case:** Pre-production testing, QA validation, performance testing

---

### Production (Basic) - Single-AZ

**Configuration:**
```hcl
instance_class = "db.t3.medium"
allocated_storage = 100
multi_az = false
backup_retention_period = 30
```

**Monthly Cost Breakdown:**
```
Component                          Qty    Rate/Unit    Monthly Cost
─────────────────────────────────────────────────────────────────────
RDS Instance (db.t3.medium)        730h   $0.068/hr    $49.64
RDS Storage (GP SSD)               100GB  $0.115/GB    $11.50
Backup Storage (30 days)           150GB  $0.095/GB    $14.25
IOPS (baseline included)           0      $0.10/IOPS   $0.00
Data Transfer Out                  20GB   $0.09/GB     $1.80
CloudWatch Enhanced Monitoring     1mo    $3.50/mo     $3.50
CloudWatch Logs                    5GB    $0.50/GB     $2.50
─────────────────────────────────────────────────────────────────────
TOTAL                                                  $83.19/month
                                                       $998.28/year
```

**Use Case:** Small production workloads, acceptable downtime, cost-sensitive

---

### Production (High Availability) - Multi-AZ

**Configuration:**
```hcl
instance_class = "db.r6g.large"
allocated_storage = 100
multi_az = true
backup_retention_period = 30
deletion_protection = true
```

**Monthly Cost Breakdown:**
```
Component                          Qty    Rate/Unit    Monthly Cost
─────────────────────────────────────────────────────────────────────
RDS Instance (db.r6g.large)        730h   $0.192/hr    $140.16
Multi-AZ Standby (same instance)   730h   $0.192/hr    $140.16
RDS Storage (GP SSD) - Primary     100GB  $0.115/GB    $11.50
RDS Storage (GP SSD) - Standby     100GB  $0.115/GB    $11.50
Backup Storage (30 days)           150GB  $0.095/GB    $14.25
Data Transfer (cross-AZ sync)      100GB  $0.01/GB     $1.00
Data Transfer Out                  50GB   $0.09/GB     $4.50
CloudWatch Enhanced Monitoring     1mo    $7.00/mo     $7.00
CloudWatch Logs                    10GB   $0.50/GB     $5.00
Performance Insights               1mo    $5.00/mo     $5.00
─────────────────────────────────────────────────────────────────────
TOTAL                                                  $340.07/month
                                                       $4,080.84/year
```

**Use Case:** Mission-critical workloads, 99.95% uptime SLA, automatic failover

---

### Production (Premium) - High Performance

**Configuration:**
```hcl
instance_class = "db.r6g.xlarge"
allocated_storage = 500
max_allocated_storage = 1000
multi_az = true
backup_retention_period = 30
deletion_protection = true
```

**Monthly Cost Breakdown:**
```
Component                          Qty    Rate/Unit    Monthly Cost
─────────────────────────────────────────────────────────────────────
RDS Instance (db.r6g.xlarge)       730h   $0.384/hr    $280.32
Multi-AZ Standby                   730h   $0.384/hr    $280.32
RDS Storage (GP SSD) - Primary     500GB  $0.115/GB    $57.50
RDS Storage (GP SSD) - Standby     500GB  $0.115/GB    $57.50
Backup Storage (30 days)           750GB  $0.095/GB    $71.25
Data Transfer (cross-AZ sync)      500GB  $0.01/GB     $5.00
Data Transfer Out                  100GB  $0.09/GB     $9.00
CloudWatch Enhanced Monitoring     1mo    $7.00/mo     $7.00
CloudWatch Logs                    20GB   $0.50/GB     $10.00
Performance Insights               1mo    $5.00/mo     $5.00
─────────────────────────────────────────────────────────────────────
TOTAL                                                  $782.89/month
                                                       $9,394.68/year
```

**Use Case:** High-traffic applications, large datasets, performance-critical workloads

---

## Cost Optimization Strategies

### 1. Reserved Instances (1-Year Commitment)

**Savings:** 30-40% on compute costs

| Instance Type | On-Demand | Reserved (1yr) | Savings |
|---------------|-----------|----------------|---------|
| db.t3.micro | $12.41/mo | $7.45/mo | 40% |
| db.t3.small | $24.82/mo | $14.89/mo | 40% |
| db.t3.medium | $49.64/mo | $29.78/mo | 40% |
| db.r6g.large | $140.16/mo | $84.10/mo | 40% |

**When to use:** Predictable workloads running 24/7

---

### 2. Savings Plans (3-Year Commitment)

**Savings:** 50-60% on compute costs

| Instance Type | On-Demand | Savings Plan (3yr) | Savings |
|---------------|-----------|---------------------|---------|
| db.t3.micro | $12.41/mo | $5.46/mo | 56% |
| db.t3.small | $24.82/mo | $10.93/mo | 56% |
| db.t3.medium | $49.64/mo | $21.85/mo | 56% |
| db.r6g.large | $140.16/mo | $61.67/mo | 56% |

**When to use:** Long-term predictable workloads

---

### 3. Right-Sizing Instances

**Example:** db.r6g.large → db.r6g.medium (based on actual metrics)

```
Before:  db.r6g.large  (16 GB RAM) = $140/month
After:   db.r6g.medium (8 GB RAM)  = $70/month
Savings: $70/month = $840/year
```

**How to identify:**
- Monitor CloudWatch CPU (target <70% average)
- Track memory utilization (target <80%)
- Review connection count (should not approach max)

---

### 4. Storage Optimization

**Strategy:** Start small, enable auto-scaling

```hcl
allocated_storage     = 20   # Start small
max_allocated_storage = 100  # Auto-scale as needed
```

**Cost Impact:**
```
Scenario A (Over-provisioned): 500 GB allocated = $57.50/month
Scenario B (Right-sized):       20 GB + auto-scale = $2.30/month initially
Savings:                        $55.20/month until actually needed
```

---

### 5. Backup Retention Optimization

**Example:** Reduce backup retention in non-production

```
Development:  7 days  → 1 day   = -75% backup storage costs
Staging:      30 days → 7 days  = -77% backup storage costs
```

**Cost Impact (100 GB database):**
```
30-day retention: 100GB × 30 days × $0.095/GB = $285/month
7-day retention:  100GB × 7 days × $0.095/GB  = $66.50/month
Savings:                                        $218.50/month
```

---

### 6. Schedule Non-Production Environments

**Strategy:** Shutdown dev/staging during nights and weekends

```bash
# Automation example
# Workdays: 8am-8pm (12 hours/day × 5 days = 60 hours/week)
# vs. Always-on (168 hours/week)
# Savings: 64% reduction in runtime

Scenario: db.t3.small
On-Demand (always-on):     $24.82/month
Scheduled (60hrs/week):    $8.94/month
Savings:                   $15.88/month (64%)
```

---

## Cost Comparison: Multi-AZ vs Single-AZ

### Availability vs Cost Trade-off

| Configuration | Monthly Cost | Availability | Failover Time |
|---------------|--------------|--------------|---------------|
| Single-AZ | $70 | 99% | Manual (hours) |
| Multi-AZ | $140 | 99.95% | Automatic (<60s) |
| **Extra Cost** | **+$70 (100%)** | **+0.95%** | **Instant** |

**Break-even Analysis:**

```
Cost of downtime per hour: $10,000
Expected downtime improvement: 4.38 hours/year (99% → 99.95%)

Annual Multi-AZ cost:     $840
Annual downtime savings:  $43,800 (4.38 hrs × $10K)
Net benefit:              $42,960/year

ROI: 5,100%
```

**Decision Matrix:**
- Downtime cost < $100/hour → Single-AZ acceptable
- Downtime cost > $1,000/hour → Multi-AZ strongly recommended
- Downtime cost > $10,000/hour → Multi-AZ + DR mandatory

---

## Interactive Cost Calculator

### Formula

```
Monthly Cost =
  (Instance Hours × Hourly Rate × Multi-AZ Multiplier) +
  (Storage GB × $0.115) +
  (Backup GB × $0.095) +
  (Data Transfer GB × $0.09) +
  (Enhanced Monitoring × $3.50)

Where:
  Instance Hours = 730 (monthly average)
  Multi-AZ Multiplier = 2 if multi_az=true, else 1
  Backup GB = Storage GB × Backup Retention Days × Change Rate
  Change Rate = typically 0.1 to 0.3 (10-30% daily change)
```

### Example Calculation

**Inputs:**
```
Instance:         db.r6g.large ($0.192/hr)
Storage:          200 GB
Multi-AZ:         true
Backup Retention: 30 days
Change Rate:      20%
Data Transfer:    100 GB/month
```

**Calculation:**
```
Instance:   730 hrs × $0.192/hr × 2 (Multi-AZ) = $280.32
Storage:    200 GB × $0.115 × 2 (Multi-AZ)     = $46.00
Backups:    200 GB × 30 days × 0.2 × $0.095   = $114.00
Transfer:   100 GB × $0.09                     = $9.00
Monitoring: $7.00 (Enhanced)                   = $7.00
──────────────────────────────────────────────────────
TOTAL:                                          $456.32/month
```

---

## Cost Projection Over Time

### 3-Year TCO Comparison

**Scenario:** Production database with moderate growth

```
Year 1:
  Instance: db.r6g.large (Multi-AZ)
  Storage:  100 GB → 200 GB (auto-scale)
  Cost:     $340/mo × 12 = $4,080

Year 2:
  Instance: db.r6g.large (Multi-AZ)
  Storage:  200 GB → 350 GB (auto-scale)
  Cost:     $385/mo × 12 = $4,620

Year 3:
  Instance: db.r6g.xlarge (upgraded)
  Storage:  350 GB → 500 GB (auto-scale)
  Cost:     $630/mo × 12 = $7,560

──────────────────────────────────────
3-Year Total:            $16,260

With Reserved Instances (40% savings):
3-Year Total:            $9,756
Savings:                 $6,504 (40%)
```

---

## Cost Alerts & Monitoring

### Recommended CloudWatch Budget Alarms

```hcl
# Example budget configuration
Development:   Alert if > $25/month
Staging:       Alert if > $50/month
Production:    Alert if > $400/month
```

### Cost Anomaly Detection

Set up AWS Cost Anomaly Detection:
```
Threshold: 20% increase from baseline
Notification: Email + Slack
Review: Weekly cost reports
```

---

## External Cost Tools

### Infracost Integration

```bash
# Install infracost
brew install infracost

# Generate cost estimate
infracost breakdown --path .

# Compare changes
infracost diff --path .
```

**Example Output:**
```
Project: RDS Database Module

 Name                              Quantity  Unit         Monthly Cost

 aws_db_instance.this
 ├─ Database instance              730       hours             $140.16
 ├─ Storage (general purpose SSD)  100       GB                 $11.50
 └─ Multi-AZ deployment            730       hours             $140.16

 OVERALL TOTAL                                                 $291.82
```

---

## Cost Optimization Checklist

### Before Deployment
- [ ] Choose appropriate instance size based on requirements
- [ ] Enable auto-scaling storage (avoid over-provisioning)
- [ ] Set backup retention based on compliance needs
- [ ] Consider reserved instances for predictable workloads
- [ ] Review multi-AZ necessity (dev/staging vs production)

### After Deployment
- [ ] Monitor CloudWatch metrics (CPU, memory, connections)
- [ ] Set up cost alerts and budgets
- [ ] Review AWS Cost Explorer monthly
- [ ] Identify unused or idle databases
- [ ] Consider upgrading to Graviton instances (ARM, 20% cheaper)

### Quarterly Review
- [ ] Right-size instances based on actual usage
- [ ] Review backup retention and storage costs
- [ ] Evaluate reserved instance or savings plan options
- [ ] Check for new instance types or pricing options
- [ ] Document cost optimization wins

---

## Real-World Cost Examples

### Startup (Pre-Revenue)
```
Environment: Single production database
Instance:    db.t3.small (Multi-AZ)
Storage:     20 GB
Cost:        ~$60/month
Strategy:    Minimal viable setup, scale as needed
```

### Small Business (10K users)
```
Environment: Prod + staging
Instances:   db.t3.medium (Multi-AZ) + db.t3.small (single-AZ)
Storage:     100 GB + 20 GB
Cost:        ~$200/month
Strategy:    HA for prod, cost-optimize staging
```

### Enterprise (1M+ users)
```
Environment: Prod (Multi-AZ) + 2 read replicas + staging + dev
Instances:   db.r6g.2xlarge (Multi-AZ) + 2× db.r6g.large + db.t3.medium + db.t3.small
Storage:     1 TB + 1 TB + 1 TB + 100 GB + 20 GB
Cost:        ~$2,500/month
Strategy:    Reserved instances, read replicas for scaling
```

---

## Summary

### Key Takeaways

1. **Start Small:** Begin with t3 instances, scale as needed
2. **Enable Auto-Scaling:** Storage grows automatically, no over-provisioning
3. **Multi-AZ for Production:** Extra cost is insurance against downtime
4. **Right-Size Regularly:** Monitor metrics, adjust instance size quarterly
5. **Use Reserved Instances:** 30-60% savings for predictable workloads
6. **Optimize Backups:** Match retention to compliance requirements
7. **Schedule Non-Production:** Shutdown dev/staging when not in use

### Cost Range Summary

| Workload Size | Configuration | Monthly Cost | Annual Cost |
|---------------|---------------|--------------|-------------|
| **Minimal** | Single-AZ, t3.micro | $15 | $180 |
| **Small** | Single-AZ, t3.small | $40 | $480 |
| **Medium** | Multi-AZ, t3.medium | $170 | $2,040 |
| **Large** | Multi-AZ, r6g.large | $340 | $4,080 |
| **Enterprise** | Multi-AZ, r6g.xlarge | $700 | $8,400 |

---

*Cost Calculator v1.0 - Last Updated: January 2025*
*Pricing based on AWS US-West-2 region. Actual costs may vary.*
