# Deployment Guide - P11 Serverless API Gateway

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.11+** installed
4. **Git** (optional, for version control)

### AWS Permissions Required

The deploying user must have permissions for:
- CloudFormation (create/update/delete stacks)
- Lambda (create/update functions)
- API Gateway (create/manage APIs)
- DynamoDB (create/manage tables)
- IAM (create roles)
- CloudWatch (create log groups)

## Installation

### 1. Clone/Download the Project

```bash
cd /home/user/Portfolio-Project/projects-new/P11-serverless-api-gateway
```

### 2. Configure AWS Credentials

```bash
# Option 1: Use named profile
aws configure --profile your-profile-name

# Option 2: Use environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 3. Install Project Dependencies

```bash
# Install all Python dependencies
make install

# Or manually:
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings (optional for dev deployment)
nano .env
```

## Deployment Options

### Option 1: Simple Dev Deployment (Recommended for Testing)

```bash
# Deploy to development environment
make deploy ENVIRONMENT=dev

# This will:
# - Build the SAM template
# - Create CloudFormation stack named "serverless-api-gateway-dev"
# - Deploy all Lambda functions
# - Create DynamoDB table
# - Setup API Gateway
# - Configure CloudWatch logging
```

### Option 2: Staged Deployment (Recommended for Production)

```bash
# Deploy to staging environment
make deploy ENVIRONMENT=staging

# Deploy to production environment
make deploy ENVIRONMENT=prod
```

### Option 3: Custom Deployment

```bash
# Custom stack name and region
make deploy \
  ENVIRONMENT=prod \
  AWS_REGION=us-west-2 \
  STACK_NAME=my-custom-api-stack
```

## Step-by-Step Deployment Process

### Step 1: Build the Application

```bash
# The deploy command does this automatically, but you can also do it manually:
sam build
```

This creates `.aws-sam/build/` directory with processed template and functions.

### Step 2: Deploy to AWS

```bash
# Interactive deployment (recommended first time)
sam deploy --guided

# Or use the Makefile with saved configuration:
make deploy ENVIRONMENT=dev
```

During guided deployment, you'll be asked about:
- Stack name
- AWS region
- Parameter values
- CloudFormation capabilities (auto-confirmed)

### Step 3: Wait for Deployment

Deployment typically takes 2-5 minutes. You'll see output like:

```
CloudFormation stack change set
Operation                  LogicalResourceId        ResourceType             Replacement
+ Add                      ItemsTable               AWS::DynamoDB::Table     N/A
+ Add                      LambdaExecutionRole      AWS::IAM::Role           N/A
+ Add                      CreateItemFunction       AWS::Lambda::Function    N/A
...
```

### Step 4: Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name serverless-api-gateway-dev \
  --query 'Stacks[0].StackStatus'

# Should output: CREATE_COMPLETE or UPDATE_COMPLETE
```

### Step 5: Get the API Endpoint

```bash
# Automatic using Makefile:
make endpoint ENVIRONMENT=dev

# Or manually:
aws cloudformation describe-stacks \
  --stack-name serverless-api-gateway-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ItemsApiEndpoint`].OutputValue' \
  --output text
```

### Step 6: Test the API

```bash
# Create an item
ENDPOINT=$(make endpoint ENVIRONMENT=dev)
curl -X POST "https://${ENDPOINT}/items" \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Item",
    "description": "Testing the deployment",
    "price": 29.99
  }'
```

## Environment-Specific Configurations

### Development Environment (default)

- **Auto-scaling**: Pay-per-request (no minimum cost)
- **Logging retention**: 7 days
- **Backup**: Disabled
- **API Key**: dev-key-12345
- **Stack name**: serverless-api-gateway-dev

Deploy with:
```bash
make deploy ENVIRONMENT=dev
```

### Staging Environment

Same as development but on staging stack:
```bash
make deploy ENVIRONMENT=staging
```

### Production Environment

- **Auto-scaling**: Provisioned (5 RCU/5 WCU DynamoDB)
- **Logging retention**: 30 days
- **Backup**: Point-in-time recovery enabled
- **API Key**: Should be changed (update in .env)
- **Stack name**: serverless-api-gateway-prod

Deploy with:
```bash
make deploy ENVIRONMENT=prod AWS_REGION=us-east-1
```

**Important**: Update the `ALLOWED_API_KEYS` before production deployment.

## Managing Deployments

### View Stack Information

```bash
# Show all outputs
make outputs ENVIRONMENT=dev

# Show specific output
aws cloudformation describe-stacks \
  --stack-name serverless-api-gateway-dev \
  --query 'Stacks[0].Outputs'
```

### Update Deployment

To update after code changes:

```bash
# Code changes are automatically included
make deploy ENVIRONMENT=dev

# Or manually:
sam build && sam deploy
```

### Delete Deployment (Cleanup)

**Warning**: This will delete all resources and data!

```bash
# Using Makefile (will ask for confirmation):
make destroy ENVIRONMENT=dev

# Or manually:
aws cloudformation delete-stack \
  --stack-name serverless-api-gateway-dev
```

To verify deletion:
```bash
aws cloudformation describe-stacks \
  --stack-name serverless-api-gateway-dev \
  --query 'Stacks[0].StackStatus'

# Will show: DELETE_IN_PROGRESS, then DELETE_COMPLETE
```

## Troubleshooting

### Common Errors

#### "You must specify a region"

```bash
# Fix: Export AWS region or add to command
export AWS_DEFAULT_REGION=us-east-1
make deploy ENVIRONMENT=dev AWS_REGION=us-east-1
```

#### "User is not authorized to perform: cloudformation:CreateStack"

```bash
# Fix: Ensure your IAM user has CloudFormation permissions
# Grant user the CloudFormationFullAccess policy or create custom policy
```

#### "Bucket does not exist" or "Access Denied" during SAM deployment

```bash
# Fix: SAM needs an S3 bucket for artifacts
# Create one and specify in deployment:
aws s3 mb s3://my-sam-artifacts-bucket
sam deploy --s3-bucket my-sam-artifacts-bucket
```

#### Lambda Function Timeout

If Lambda functions timeout (especially on first invocation):
- Cold start is normal (~1-2 seconds)
- Increase timeout in `template.yaml`:
  ```yaml
  Timeout: 60  # Increase from 30
  ```

#### DynamoDB Throughput Exceeded

If you exceed provisioned capacity:
- Switch to PAY_PER_REQUEST in `template.yaml`
- Or increase ProvisionedThroughput

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export AWS_DEBUG=true

# Run deployment with debug
sam deploy --debug 2>&1 | tee deployment.log

# Check Lambda logs
aws logs tail /aws/lambda/create-item-dev --follow
```

### Check CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/create-item-dev --follow

# View all Lambda logs
aws logs describe-log-groups --query 'logGroups[*].logGroupName'
```

## Cost Management

### Estimate Costs

For development environment (pay-per-request):
- API Gateway: ~$3.50 per million requests
- Lambda: ~$0.20 per 1 million requests (128MB)
- DynamoDB: ~$1.25 per million write units
- Minimal free tier available

### Cost Optimization Tips

1. **Use pay-per-request for dev/test**:
   - Set `BillingMode: PAY_PER_REQUEST` in template.yaml

2. **Reduce log retention**:
   ```yaml
   RetentionInDays: 3  # For development
   ```

3. **Delete unused stacks**:
   ```bash
   make destroy ENVIRONMENT=staging
   ```

4. **Monitor with CloudWatch**:
   - Set up billing alerts in AWS Billing console
   - Review Lambda execution duration and memory usage

## Post-Deployment

### Update API Keys

```bash
# Update in your environment
export ALLOWED_API_KEYS="new-key-1,new-key-2"

# Redeploy to apply changes
make deploy ENVIRONMENT=prod
```

### Monitor Performance

```bash
# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=create-item-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Enable X-Ray Tracing

Tracing is already enabled in the SAM template. View traces:

1. Go to AWS X-Ray console
2. Click "Service map"
3. Click on Lambda or API Gateway nodes
4. View trace details including:
   - Request flow
   - DynamoDB operations
   - Response times

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: make test
      - name: Deploy
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: make deploy ENVIRONMENT=prod
```

## Next Steps

1. **Monitor**: Set up CloudWatch alarms
2. **Scale**: Adjust Lambda memory and DynamoDB capacity
3. **Secure**: Update API keys and implement VPC
4. **Backup**: Enable DynamoDB Point-in-Time Recovery
5. **Logging**: Configure structured logging with JSON

---

For more information, see:
- `QUICKSTART.md` - 5-minute guide
- `IMPLEMENTATION.md` - Detailed architecture
- `Makefile` - Available commands
