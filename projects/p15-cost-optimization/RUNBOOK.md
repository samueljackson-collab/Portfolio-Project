# Runbook — P15 (Cloud Cost Optimization)

## Overview

Production operations runbook for the P15 Cloud Cost Optimization platform. This runbook covers cost analysis, rightsizing recommendations, reserved instance planning, anomaly detection, budget management, and FinOps practices for AWS cloud infrastructure.

**System Components:**
- AWS Cost and Usage Reports (CUR) in S3
- Amazon Athena for cost analysis queries
- Cost anomaly detection system
- Rightsizing recommendation engine
- Reserved Instance / Savings Plan advisor
- Budget alerts and notifications
- Cost optimization dashboard

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cost reduction** | 20% year-over-year | Monthly cost comparison |
| **Reserved Instance coverage** | 80% for stable workloads | RI coverage ratio |
| **Rightsizing completion rate** | 90% of recommendations | Implemented recommendations / total |
| **Cost anomaly detection time** | < 24 hours | Time from anomaly to alert |
| **Budget alert accuracy** | 95% no false positives | Accurate alerts / total alerts |
| **Idle resource identification** | 100% within 7 days | Time to detect unused resources |

---

## Dashboards & Alerts

### Dashboards

#### Cost Overview Dashboard
```bash
# Get current month's spend
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date -d tomorrow +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost UnblendedCost \
  --output table

# Compare to last month
LAST_MONTH_START=$(date -d "$(date +%Y-%m-01) -1 month" +%Y-%m-%d)
LAST_MONTH_END=$(date +%Y-%m-01)
aws ce get-cost-and-usage \
  --time-period Start=$LAST_MONTH_START,End=$LAST_MONTH_END \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --output table

# Get spend by service
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date -d tomorrow +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output table | head -20

# Get daily cost trend
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date -d tomorrow +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --output json | jq '.ResultsByTime[] | {Date: .TimePeriod.Start, Cost: .Total.BlendedCost.Amount}'
```

#### Rightsizing Dashboard
```bash
# Get rightsizing recommendations
aws ce get-rightsizing-recommendation \
  --service AmazonEC2 \
  --output table

# Count recommendations
aws ce get-rightsizing-recommendation \
  --service AmazonEC2 \
  --query 'length(RightsizingRecommendations)' \
  --output text

# Estimate savings
aws ce get-rightsizing-recommendation \
  --service AmazonEC2 \
  --query 'SummaryMetrics.EstimatedTotalMonthlySavingsAmount' \
  --output text
```

#### Reserved Instance Dashboard
```bash
# Get RI coverage
aws ce get-reservation-coverage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --output table

# Get RI utilization
aws ce get-reservation-utilization \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --output table

# Get RI purchase recommendations
aws ce get-reservation-purchase-recommendation \
  --service AmazonEC2 \
  --lookback-period-in-days SIXTY_DAYS \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --output table
```

#### Cost Anomaly Dashboard
```bash
# Get cost anomalies
aws ce get-anomalies \
  --date-interval Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --max-results 50 \
  --output table

# Get anomaly monitors
aws ce get-anomaly-monitors --output table

# Get anomaly subscriptions
aws ce get-anomaly-subscriptions --output table
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Cost anomaly > $10,000 spike | Immediate | Investigate and stop runaway resources |
| **P0** | Monthly budget exceeded by 50% | Immediate | Emergency cost reduction measures |
| **P1** | Cost anomaly > $1,000 spike | 4 hours | Investigate and implement fixes |
| **P1** | Projected to exceed monthly budget | 24 hours | Review and optimize resources |
| **P2** | RI utilization < 50% | 48 hours | Review RI purchases, consider modifying |
| **P2** | Idle resources detected | 48 hours | Review and terminate/stop |
| **P3** | Rightsizing recommendations available | 1 week | Review and implement recommendations |

#### Alert Queries

```bash
# Check for cost spikes in last 24 hours
YESTERDAY_COST=$(aws ce get-cost-and-usage \
  --time-period Start=$(date -d '2 days ago' +%Y-%m-%d),End=$(date -d '1 day ago' +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text)

TODAY_COST=$(aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 day ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text)

INCREASE=$(echo "scale=2; ($TODAY_COST - $YESTERDAY_COST) / $YESTERDAY_COST * 100" | bc)
echo "Cost change: ${INCREASE}%"
[ $(echo "$INCREASE > 20" | bc) -eq 1 ] && echo "ALERT: Significant cost increase!"

# Check budget status
aws budgets describe-budgets \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --query 'Budgets[*].{Name:BudgetName,Limit:BudgetLimit.Amount,Actual:CalculatedSpend.ActualSpend.Amount}' \
  --output table

# Check for untagged resources
aws resourcegroupstaggingapi get-resources \
  --resource-type-filters ec2:instance \
  --query 'ResourceTagMappingList[?Tags==`[]`]' | \
  jq 'length' | \
  awk '{if($1>0) print "ALERT: "$1" untagged EC2 instances found"}'
```

---

## Standard Operations

### Cost Analysis

#### Run Monthly Cost Report
```bash
# Generate monthly cost report
make analyze-costs

# Or manually:
./scripts/generate-cost-report.sh $(date +%Y-%m)

# Report includes:
# - Total spend by service
# - Cost trends
# - Top 10 most expensive resources
# - Month-over-month comparison
# - Budget vs actual

# View report
cat reports/cost-report-$(date +%Y-%m).txt
```

#### Query CUR Data with Athena
```bash
# Common cost analysis queries

# 1. Top 10 most expensive services
aws athena start-query-execution \
  --query-string "
SELECT
  line_item_product_code,
  SUM(line_item_unblended_cost) as cost
FROM ${ATHENA_DATABASE}.${CUR_TABLE}
WHERE year='$(date +%Y)' AND month='$(date +%m)'
GROUP BY line_item_product_code
ORDER BY cost DESC
LIMIT 10
" \
  --result-configuration OutputLocation=s3://${ATHENA_RESULTS_BUCKET}/ \
  --query-execution-context Database=${ATHENA_DATABASE}

# 2. Daily cost trend
aws athena start-query-execution \
  --query-string "
SELECT
  line_item_usage_start_date,
  SUM(line_item_unblended_cost) as daily_cost
FROM ${ATHENA_DATABASE}.${CUR_TABLE}
WHERE year='$(date +%Y)' AND month='$(date +%m)'
GROUP BY line_item_usage_start_date
ORDER BY line_item_usage_start_date
" \
  --result-configuration OutputLocation=s3://${ATHENA_RESULTS_BUCKET}/ \
  --query-execution-context Database=${ATHENA_DATABASE}

# 3. Cost by tag (Environment)
aws athena start-query-execution \
  --query-string "
SELECT
  resource_tags_user_environment as environment,
  SUM(line_item_unblended_cost) as cost
FROM ${ATHENA_DATABASE}.${CUR_TABLE}
WHERE year='$(date +%Y)' AND month='$(date +%m)'
GROUP BY resource_tags_user_environment
ORDER BY cost DESC
" \
  --result-configuration OutputLocation=s3://${ATHENA_RESULTS_BUCKET}/ \
  --query-execution-context Database=${ATHENA_DATABASE}

# Get query results
QUERY_ID=<query-execution-id>
aws athena get-query-results --query-execution-id $QUERY_ID --output table
```

#### Identify Idle Resources
```bash
# Run idle resource detection
./scripts/find-idle-resources.sh

# Script checks for:
# - Stopped EC2 instances
# - Unattached EBS volumes
# - Unused Elastic IPs
# - Old snapshots
# - Unused load balancers
# - Unused RDS instances

# View idle resources report
cat reports/idle-resources-$(date +%Y-%m-%d).txt

# Estimated savings
tail -1 reports/idle-resources-$(date +%Y-%m-%d).txt
```

### Rightsizing Operations

#### Review Rightsizing Recommendations
```bash
# Get all rightsizing recommendations
aws ce get-rightsizing-recommendation \
  --service AmazonEC2 \
  --output json > reports/rightsizing-$(date +%Y-%m-%d).json

# View summary
cat reports/rightsizing-$(date +%Y-%m-%d).json | jq '.SummaryMetrics'

# View recommendations
cat reports/rightsizing-$(date +%Y-%m-%d).json | jq '.RightsizingRecommendations[] | {
  InstanceId: .CurrentInstance.ResourceId,
  CurrentType: .CurrentInstance.InstanceType,
  RecommendedType: .ModifyRecommendationDetail.TargetInstances[0].InstanceType,
  MonthlySavings: .ModifyRecommendationDetail.TargetInstances[0].EstimatedMonthlySavings
}'
```

#### Implement Rightsizing Recommendation
```bash
# Rightsize specific instance
INSTANCE_ID=i-1234567890abcdef0
NEW_TYPE=t3.medium

# 1. Get current instance details
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].{Type:InstanceType,State:State.Name}' \
  --output table

# 2. Stop instance
echo "Stopping instance $INSTANCE_ID..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID

# Wait for instance to stop
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

# 3. Modify instance type
echo "Changing instance type to $NEW_TYPE..."
aws ec2 modify-instance-attribute \
  --instance-id $INSTANCE_ID \
  --instance-type $NEW_TYPE

# 4. Start instance
echo "Starting instance..."
aws ec2 start-instances --instance-ids $INSTANCE_ID

# Wait for instance to start
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# 5. Verify new instance type
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].InstanceType' \
  --output text

# 6. Monitor for issues
echo "Monitoring instance health..."
sleep 60
aws ec2 describe-instance-status --instance-ids $INSTANCE_ID --output table

# 7. Document change
echo "$(date): Rightsized $INSTANCE_ID to $NEW_TYPE" >> logs/rightsizing-changes.log
```

#### Bulk Rightsizing
```bash
# Rightsize multiple instances based on recommendations
./scripts/bulk-rightsize.sh reports/rightsizing-$(date +%Y-%m-%d).json

# Script performs:
# 1. Validates recommendations
# 2. Schedules changes during maintenance window
# 3. Stops instances one at a time
# 4. Modifies instance types
# 5. Starts instances
# 6. Validates health
# 7. Documents changes

# Monitor progress
tail -f logs/bulk-rightsizing-$(date +%Y-%m-%d).log
```

### Reserved Instance Management

#### Review RI Recommendations
```bash
# Get RI purchase recommendations for EC2
aws ce get-reservation-purchase-recommendation \
  --service AmazonEC2 \
  --lookback-period-in-days SIXTY_DAYS \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --output json > reports/ri-recommendations-ec2-$(date +%Y-%m-%d).json

# View summary
cat reports/ri-recommendations-ec2-$(date +%Y-%m-%d).json | jq '.Metadata'

# View recommendations
cat reports/ri-recommendations-ec2-$(date +%Y-%m-%d).json | jq '.Recommendations[] | {
  InstanceType: .RecommendationDetails.AmazonEC2ReservedInstancesDetails.InstanceType,
  Quantity: .RecommendationDetails.AmazonEC2ReservedInstancesDetails.RecommendedNumberOfInstancesToPurchase,
  EstimatedMonthlySavings: .RecommendationDetails.EstimatedMonthlySavingsAmount,
  UpfrontCost: .RecommendationDetails.UpfrontCost
}'

# Get RDS RI recommendations
aws ce get-reservation-purchase-recommendation \
  --service AmazonRDS \
  --lookback-period-in-days SIXTY_DAYS \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --output json > reports/ri-recommendations-rds-$(date +%Y-%m-%d).json
```

#### Purchase Reserved Instances
```bash
# Purchase EC2 Reserved Instances
# CAUTION: This is a financial commitment!

# 1. Review recommendation
INSTANCE_TYPE=t3.large
QUANTITY=10
TERM_YEARS=1

# 2. Get available offerings
aws ec2 describe-reserved-instances-offerings \
  --instance-type $INSTANCE_TYPE \
  --instance-tenancy default \
  --offering-class standard \
  --product-description "Linux/UNIX" \
  --filters Name=duration,Values=31536000 Name=offering-type,Values=No Upfront \
  --output table

# 3. Purchase RI
OFFERING_ID=<reserved-instances-offering-id>
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id $OFFERING_ID \
  --instance-count $QUANTITY

# 4. Verify purchase
aws ec2 describe-reserved-instances \
  --filters Name=state,Values=active \
  --output table

# 5. Document purchase
cat >> logs/ri-purchases.log <<EOF
Date: $(date)
Instance Type: $INSTANCE_TYPE
Quantity: $QUANTITY
Term: $TERM_YEARS year(s)
Offering ID: $OFFERING_ID
EOF
```

#### Monitor RI Utilization
```bash
# Check RI utilization
aws ce get-reservation-utilization \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --output table

# Check RI coverage
aws ce get-reservation-coverage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --output table

# Detailed RI usage
aws ce get-reservation-utilization \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --group-by Type=DIMENSION,Key=SUBSCRIPTION_ID \
  --output json | jq '.UtilizationsByTime[] | {
    Date: .TimePeriod.Start,
    Utilization: .Total.UtilizationPercentage,
    UnusedHours: .Total.TotalUnusedHours
  }'
```

### Savings Plan Management

#### Review Savings Plan Recommendations
```bash
# Get Savings Plan purchase recommendations
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days SIXTY_DAYS \
  --output json > reports/sp-recommendations-$(date +%Y-%m-%d).json

# View recommendations
cat reports/sp-recommendations-$(date +%Y-%m-%d).json | jq '.SavingsPlansPurchaseRecommendation.SavingsPlansPurchaseRecommendationDetails[] | {
  HourlyCommitment: .HourlyCommitmentToPurchase,
  EstimatedMonthlySavings: .EstimatedMonthlySavingsAmount,
  EstimatedROI: .EstimatedROI
}'
```

#### Monitor Savings Plan Utilization
```bash
# Check Savings Plan utilization
aws ce get-savings-plans-utilization \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --output table

# Check Savings Plan coverage
aws ce get-savings-plans-coverage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --output table
```

### Budget Management

#### Create Budget
```bash
# Create monthly budget with alerts
cat > budget-definition.json <<EOF
{
  "BudgetName": "monthly-budget-$(date +%Y-%m)",
  "BudgetLimit": {
    "Amount": "10000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {},
  "CostTypes": {
    "IncludeTax": true,
    "IncludeSubscription": true,
    "UseBlended": false,
    "IncludeRefund": false,
    "IncludeCredit": false,
    "IncludeUpfront": true,
    "IncludeRecurring": true,
    "IncludeOtherSubscription": true,
    "IncludeSupport": true,
    "IncludeDiscount": true,
    "UseAmortized": false
  }
}
EOF

aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget-definition.json

# Create budget alerts
cat > budget-notification.json <<EOF
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
      "Address": "ops@example.com"
    }
  ]
}
EOF

aws budgets create-notification \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget-name "monthly-budget-$(date +%Y-%m)" \
  --notification file://budget-notification.json
```

#### Monitor Budgets
```bash
# View all budgets
aws budgets describe-budgets \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --output table

# View budget details
aws budgets describe-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget-name monthly-budget-$(date +%Y-%m) \
  --output table

# Check budget alerts
aws budgets describe-notifications-for-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget-name monthly-budget-$(date +%Y-%m) \
  --output table
```

### Cost Anomaly Detection

#### Configure Anomaly Detection
```bash
# Create anomaly monitor
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "production-cost-monitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'

# Create anomaly subscription
aws ce create-anomaly-subscription \
  --anomaly-subscription '{
    "SubscriptionName": "cost-anomaly-alerts",
    "Threshold": 100,
    "Frequency": "IMMEDIATE",
    "MonitorArnList": ["<monitor-arn>"],
    "Subscribers": [
      {
        "Type": "EMAIL",
        "Address": "ops@example.com"
      }
    ]
  }'
```

#### Review Cost Anomalies
```bash
# Get recent anomalies
aws ce get-anomalies \
  --date-interval Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --max-results 50 \
  --output json > reports/anomalies-$(date +%Y-%m-%d).json

# View anomaly details
cat reports/anomalies-$(date +%Y-%m-%d).json | jq '.Anomalies[] | {
  Service: .RootCauses[0].Service,
  Impact: .Impact.MaxImpact,
  StartDate: .AnomalyStartDate,
  EndDate: .AnomalyEndDate
}'

# Get anomaly feedback
aws ce get-anomaly-monitors --output table
```

---

## Incident Response

### Detection

**Automated Detection:**
- Budget alert notifications
- Cost anomaly alerts
- RI/SP utilization alerts

**Manual Detection:**
```bash
# Check for cost spikes
./scripts/detect-cost-spikes.sh

# Check budget status
aws budgets describe-budgets \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --query 'Budgets[*].{Name:BudgetName,Spent:CalculatedSpend.ActualSpend.Amount,Limit:BudgetLimit.Amount}'

# Check anomalies
aws ce get-anomalies \
  --date-interval Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --output table
```

### Triage

#### Severity Classification

**P0: Critical Cost Event**
- Cost anomaly > $10,000 spike
- Monthly budget exceeded by > 50%
- Runaway resource creation detected

**P1: Significant Cost Issue**
- Cost anomaly > $1,000 spike
- Projected to exceed monthly budget
- Major inefficiency detected

**P2: Cost Optimization Opportunity**
- RI utilization < 50%
- Significant rightsizing opportunities
- Idle resources accumulating

**P3: Routine Optimization**
- Minor cost trends
- Incremental optimization opportunities
- Tagging compliance issues

### Incident Response Procedures

#### P0: Runaway Resource Costs

**Immediate Actions (0-30 minutes):**
```bash
# 1. Identify the spike
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json | jq '.ResultsByTime[-1].Groups | sort_by(.Metrics.BlendedCost.Amount) | reverse | .[0:5]'

# 2. Identify specific resources
# If EC2 spike:
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[?LaunchTime>=`'$(date -d '24 hours ago' -u +%Y-%m-%dT%H:%M:%S)'`].[InstanceId,InstanceType,LaunchTime,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# If Lambda spike:
aws logs filter-log-events \
  --log-group-name /aws/lambda/ \
  --start-time $(($(date +%s - 86400) * 1000)) \
  --filter-pattern "REPORT" | \
  grep "Duration\|Billed" | wc -l

# 3. Emergency: Stop runaway resources
# Stop recently launched suspicious EC2 instances
for instance in $(aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[?LaunchTime>=`'$(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S)'`].InstanceId' --output text); do
  echo "Stopping $instance..."
  aws ec2 stop-instances --instance-ids $instance
done

# Or terminate if definitely unauthorized
# aws ec2 terminate-instances --instance-ids <instance-ids>

# 4. Disable problematic Lambda function (if Lambda spike)
FUNCTION_NAME=<problematic-function>
aws lambda put-function-concurrency \
  --function-name $FUNCTION_NAME \
  --reserved-concurrent-executions 0

# 5. Document incident
cat > logs/cost-incident-$(date +%Y%m%d-%H%M%S).log <<EOF
Cost Incident Report
Date: $(date)
Type: Runaway resources
Estimated Impact: \$XXX
Actions Taken:
- Stopped instances: [list]
- Disabled functions: [list]
EOF
```

**Investigation (30 minutes - 2 hours):**
```bash
# Analyze CloudTrail for unauthorized actions
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances \
  --start-time $(date -d '24 hours ago' -u +%Y-%m-%dT%H:%M:%S) \
  --max-results 50 \
  --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Resources:Resources[0].ResourceName}'

# Check for compromised credentials
aws iam generate-credential-report
aws iam get-credential-report

# Review cost by tag
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --group-by Type=TAG,Key=Owner \
  --metrics BlendedCost
```

**Prevention:**
```bash
# Implement preventative controls
# 1. Set up service quotas
aws service-quotas request-service-quota-increase \
  --service-code ec2 \
  --quota-code L-1216C47A \
  --desired-value 50  # Max running On-Demand instances

# 2. Enable AWS Config rules
# - required-tags
# - approved-amis-by-tag
# - ec2-instance-no-public-ip

# 3. Implement budget actions (auto-stop on threshold)
# See AWS Budgets Actions documentation
```

---

#### P1: Budget Exceeded / Projected to Exceed

**Immediate Actions (0-4 hours):**
```bash
# 1. Assess current spend
aws budgets describe-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget-name monthly-budget-$(date +%Y-%m) \
  --output table

# 2. Project end-of-month spend
DAYS_IN_MONTH=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%d)
CURRENT_DAY=$(date +%d)
CURRENT_SPEND=$(aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date -d tomorrow +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text)

PROJECTED_SPEND=$(echo "scale=2; $CURRENT_SPEND * $DAYS_IN_MONTH / $CURRENT_DAY" | bc)
echo "Current spend: \$${CURRENT_SPEND}"
echo "Projected end-of-month: \$${PROJECTED_SPEND}"

# 3. Identify top cost drivers
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date -d tomorrow +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json | jq '.ResultsByTime[0].Groups | sort_by(.Metrics.BlendedCost.Amount) | reverse | .[0:10]'

# 4. Quick wins - Stop/terminate idle resources
./scripts/stop-idle-resources.sh --execute

# 5. Implement temporary cost controls
# - Stop non-production environments overnight
# - Reduce instance sizes where possible
# - Disable non-critical services
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Cost Analysis
```bash
# Detailed cost breakdown
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date -d tomorrow +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE Type=DIMENSION,Key=USAGE_TYPE \
  --output json > reports/detailed-costs.json

# Find expensive resources
# EC2 instances by cost
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Elastic Compute Cloud - Compute"]}}' \
  --group-by Type=DIMENSION,Key=INSTANCE_TYPE \
  --metrics BlendedCost

# RDS instances by cost
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Relational Database Service"]}}' \
  --metrics BlendedCost
```

#### Resource Tagging Audit
```bash
# Find untagged resources
# EC2 instances
aws ec2 describe-instances \
  --query 'Reservations[].Instances[?Tags==`null` || !Tags[?Key==`Environment`]].InstanceId' \
  --output table

# EBS volumes
aws ec2 describe-volumes \
  --query 'Volumes[?Tags==`null` || !Tags[?Key==`Environment`]].VolumeId' \
  --output table

# S3 buckets (check for required tags)
for bucket in $(aws s3 ls | awk '{print $3}'); do
  TAGS=$(aws s3api get-bucket-tagging --bucket $bucket 2>/dev/null)
  if [ -z "$TAGS" ]; then
    echo "Untagged bucket: $bucket"
  fi
done
```

### Common Issues & Solutions

#### Issue: Unexpected cost spike

**Investigation:**
```bash
# 1. Identify service causing spike
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json | jq '.ResultsByTime[] | {Date:.TimePeriod.Start, Services:.Groups}'

# 2. Drill down into specific service
# Example for S3:
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Simple Storage Service"]}}' \
  --group-by Type=DIMENSION,Key=USAGE_TYPE \
  --metrics BlendedCost

# 3. Check CloudWatch metrics for usage spikes
# EC2 CPU spikes
# S3 data transfer
# Lambda invocations
```

---

#### Issue: Low RI utilization

**Investigation:**
```bash
# Check which RIs are underutilized
aws ce get-reservation-utilization \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --group-by Type=DIMENSION,Key=SUBSCRIPTION_ID \
  --output table

# Check instance usage patterns
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --filter '{"Dimensions":{"Key":"PURCHASE_TYPE","Values":["Reservation"]}}' \
  --group-by Type=DIMENSION,Key=INSTANCE_TYPE \
  --metrics UnblendedCost UsageQuantity
```

**Solution:**
- Modify RI (change instance type, availability zone)
- Sell unused RIs on RI Marketplace
- Adjust workload to use purchased capacity
- Consider Savings Plans for more flexibility

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check yesterday's cost
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 day ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost

# Check for new anomalies
aws ce get-anomalies \
  --date-interval Start=$(date -d '1 day ago' +%Y-%m-%d),End=$(date +%Y-%m-%d)

# Check budget status
./scripts/check-budget-status.sh
```

### Weekly Tasks
```bash
# Generate weekly cost report
./scripts/generate-cost-report.sh --period week

# Review new rightsizing recommendations
aws ce get-rightsizing-recommendation --service AmazonEC2

# Check RI/SP utilization
aws ce get-reservation-utilization \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity WEEKLY

# Find and tag untagged resources
./scripts/tag-untagged-resources.sh --dry-run

# Review idle resources
./scripts/find-idle-resources.sh
```

### Monthly Tasks
```bash
# Generate monthly cost report
make generate-report MONTH=$(date +%Y-%m)

# Review and implement rightsizing recommendations
# Target: 90% implementation rate

# Review RI/SP purchase recommendations
aws ce get-reservation-purchase-recommendation --service AmazonEC2
aws ce get-savings-plans-purchase-recommendation --savings-plans-type COMPUTE_SP

# Update cost allocation tags
aws ce update-cost-allocation-tags-status --cost-allocation-tags-status TagKey=Project,Status=Active

# Review and update budgets for next month
./scripts/update-budgets.sh --month $(date -d 'next month' +%Y-%m)

# Conduct cost optimization review meeting
# - Review month's spend
# - Discuss optimization opportunities
# - Plan next month's initiatives
```

---

## Quick Reference

### Common Commands
```bash
# Check current month spend
aws ce get-cost-and-usage --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) --granularity MONTHLY --metrics BlendedCost

# Get rightsizing recommendations
aws ce get-rightsizing-recommendation --service AmazonEC2

# Check RI utilization
aws ce get-reservation-utilization --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity MONTHLY

# Find idle resources
./scripts/find-idle-resources.sh

# Generate cost report
make generate-report
```

### Emergency Response
```bash
# P0: Stop runaway resources
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[?LaunchTime>=`'$(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S)'`].InstanceId'
# Review and stop/terminate as needed

# P1: Emergency cost reduction
./scripts/stop-idle-resources.sh --execute
./scripts/stop-non-prod-environments.sh
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** FinOps / Cloud Economics Team
- **Review Schedule:** Monthly or after significant cost events
- **Feedback:** Create issue or submit PR with updates
