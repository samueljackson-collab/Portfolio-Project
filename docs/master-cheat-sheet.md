# Portfolio Projects – Master Cheat Sheet (Expanded)

Quick reference guide for commands, configurations, architectural concepts, and refined code across more than 25 DevOps and cloud engineering portfolio projects.

---

## ☁️ 1. AWS Infrastructure Automation (CloudFormation)

Infrastructure as Code (IaC) template that provisions a scalable, resilient, and secure web application environment on AWS. It automates networking, compute, and security resources.

### Quick Deploy Script
```bash
#!/bin/bash
# A simple deployment script

# --- Variables ---
STACK_NAME="myapp-dev"
TEMPLATE_FILE="infrastructure.yaml"
AWS_REGION="us-west-2"
KEY_PAIR_NAME="my-key" # Make sure this key pair exists in your AWS account

# --- Create or Update Stack ---
echo "Deploying CloudFormation stack: $STACK_NAME..."
aws cloudformation deploy \
  --region $AWS_REGION \
  --stack-name $STACK_NAME \
  --template-file $TEMPLATE_FILE \
  --parameter-overrides \
    EnvironmentName=development \
    ProjectName=myapp \
    KeyPairName=$KEY_PAIR_NAME \
  --capabilities CAPABILITY_NAMED_IAM

# --- Wait for completion ---
echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION
echo "Stack creation successful!"

# --- Get Outputs ---
echo "Stack Outputs:"
aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION \
  --query 'Stacks[0].Outputs' --output table
```

### Core Infrastructure (`infrastructure.yaml`)
Creates a VPC with public/private subnets, an Application Load Balancer (ALB), an Auto Scaling Group, and security groups.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Deploys a scalable and redundant web application infrastructure.'

Parameters:
  EnvironmentName:
    Type: String
    Description: 'An environment name (e.g., development, production).'
    Default: 'development'
  ProjectName:
    Type: String
    Description: 'The name of the project.'
    Default: 'myapp'
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: 'Name of an existing EC2 KeyPair to enable SSH access.'

Resources:
  # --- Networking ---
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-vpc-${EnvironmentName}'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
  VPCGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-public-1'

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-private-1'

  # --- Routing ---
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
  PublicRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
  PublicSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  # --- Security ---
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: 'Allow HTTP/HTTPS traffic to ALB'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - CidrIp: 0.0.0.0/0
          IpProtocol: tcp
          FromPort: 80
          ToPort: 80
        - CidrIp: 0.0.0.0/0
          IpProtocol: tcp
          FromPort: 443
          ToPort: 443

  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: 'Allow traffic from ALB and SSH'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - SourceSecurityGroupId: !Ref ALBSecurityGroup
          IpProtocol: tcp
          FromPort: 80
          ToPort: 80
        - CidrIp: 0.0.0.0/0 # Warning: For demo only. Restrict to your IP.
          IpProtocol: tcp
          FromPort: 22
          ToPort: 22

  # --- Compute ---
  AppLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        ImageId: 'ami-0c55b159cbfafe1f0' # Amazon Linux 2 AMI
        InstanceType: 't2.micro'
        KeyName: !Ref KeyPairName
        SecurityGroupIds:
          - !Ref AppSecurityGroup
        UserData:
          Fn::Base64: |
            #!/bin/bash
            yum update -y
            yum install -y httpd
            systemctl start httpd
            systemctl enable httpd
            echo "<h1>Hello from $(hostname -f)</h1>" > /var/www/html/index.html

  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Subnets:
        - !Ref PublicSubnet1
      SecurityGroups:
        - !Ref ALBSecurityGroup

  ALBTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      VpcId: !Ref VPC
      Port: 80
      Protocol: 'HTTP'
      HealthCheckPath: '/'

  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: 'HTTP'
      DefaultActions:
        - Type: 'forward'
          TargetGroupArn: !Ref ALBTargetGroup

  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1
      LaunchTemplate:
        LaunchTemplateId: !Ref AppLaunchTemplate
        Version: !GetAtt AppLaunchTemplate.LatestVersionNumber
      MinSize: '1'
      MaxSize: '3'
      DesiredCapacity: '2'
      TargetGroupARNs:
        - !Ref ALBTargetGroup

Outputs:
  LoadBalancerDNS:
    Description: 'The DNS name of the Application Load Balancer'
    Value: !GetAtt ApplicationLoadBalancer.DNSName
```

### Troubleshooting Tips
- **CAPABILITY_NAMED_IAM**: Required because the template may create IAM resources with custom names. Acknowledge the security implications before deploying.
- **Stack Rollback**: Use the CloudFormation console "Events" tab for timestamped failure details.
- **Instance Health**: Prefer EC2 Session Manager over SSH keys. Inspect `/var/log/cloud-init-output.log` and `/var/log/messages` when troubleshooting userdata.

---

## 🔒 2. IAM Security Hardening

Implements IAM best practices by enforcing least privilege, MFA, and credential audits.

### Audit & Hardening Script
```bash
#!/bin/bash
# Script to audit and report on IAM security posture

echo "--- Listing All IAM Users ---"
aws iam list-users --query 'Users[*].[UserName,CreateDate]' --output table

echo -e "\n--- Finding Users with Active Access Keys ---"
aws iam list-users --query 'Users[*].UserName' --output text | \
  while read user; do
    aws iam list-access-keys --user-name "$user" \
      --query "AccessKeyMetadata[?Status=='Active'].[UserName,AccessKeyId,CreateDate]" \
      --output text
  done

echo -e "\n--- Generating Credential Report for Offline Analysis ---"
aws iam generate-credential-report
# Give it a moment to generate
sleep 5
aws iam get-credential-report --query 'Content' --output text | base64 -d > credential-report.csv
echo "Credential report saved to credential-report.csv"
echo "You can now analyze this file for MFA status, key age, etc."
```

### Policy Documents
**Trust Policy for an EC2 Role (`ec2-trust-policy.json`)** — Allows EC2 instances to assume the role.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "ec2.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Least Privilege S3 Policy (`s3-readonly-policy.json`)** — Grants read-only access to a specific S3 bucket.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-data-bucket",
        "arn:aws:s3:::my-app-data-bucket/*"
      ]
    }
  ]
}
```

**Force MFA Policy (`force-mfa-policy.json`)** — Denies all actions when MFA is absent.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAllExceptMFASecuredAccess",
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "iam:ListMFADevices",
        "iam:ResyncMFADevice",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### Best Practices
- ✅ **Use IAM Roles for AWS Services**: Avoid long-lived keys on compute services.
- ✅ **Enable MFA**: Critical guardrail against compromised passwords.
- ✅ **Rotate Keys Every 90 Days**: Automate the process to reduce exposure.
- ✅ **Adopt AWS SSO for Human Access**: Centralizes control via identity providers.
- ✅ **Implement SCPs**: Guardrails for all accounts in AWS Organizations.
- ✅ **Enable CloudTrail**: Capture all API activity for auditing and investigations.

---

## 🔄 5. CI/CD Pipeline with GitHub Actions

End-to-end pipeline that tests, lints, scans, builds, and deploys an application when changes reach the `main` branch.

### Workflow (`.github/workflows/ci-cd.yml`)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  DOCKER_IMAGE_NAME: my-app
  DOCKER_REGISTRY: docker.io/myusername # Change to your Docker Hub username or other registry

jobs:
  #----------------------------------------
  # Test and Lint Job
  #----------------------------------------
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint # Assumes you have a 'lint' script in package.json

      - name: Run unit tests with coverage
        run: npm test -- --coverage

      - name: Upload coverage report
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  #----------------------------------------
  # Security Scan Job
  #----------------------------------------
  security:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner on filesystem
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          ignore-unfixed: true
          format: 'table'
          severity: 'HIGH,CRITICAL'
          exit-code: '1' # Fail the build if vulnerabilities are found

  #----------------------------------------
  # Build and Push Docker Image Job
  #----------------------------------------
  build:
    needs: security
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ env.DOCKER_REGISTRY }}/${{ env.DOCKER_IMAGE_NAME }}:${{ github.sha }}, ${{ env.DOCKER_REGISTRY }}/${{ env.DOCKER_IMAGE_NAME }}:latest

  #----------------------------------------
  # Deploy to Production Job
  #----------------------------------------
  deploy:
    needs: build
    runs-on: ubuntu-latest
    # Only run this job on push events to the main branch
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://myapp.example.com
    steps:
      - name: Deploy to Kubernetes
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            # Set Kubeconfig for the cluster
            export KUBECONFIG=~/.kube/config
            # Update the deployment with the new image tag
            kubectl set image deployment/myapp-deployment myapp-container=${{ env.DOCKER_REGISTRY }}/${{ env.DOCKER_IMAGE_NAME }}:${{ github.sha }} -n production
            # Verify the rollout status
            kubectl rollout status deployment/myapp-deployment -n production
```

### Managing Secrets in GitHub
1. Navigate to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. Add values such as `DOCKER_USERNAME`, `DOCKER_PASSWORD`, and `PROD_SSH_KEY` (private key for the deployment server).

---

## 🧪 12. Selenium Web Automation

Reliable browser automation using Selenium, Python, and the Page Object Model (POM).

### Page Objects
`pages/login_page.py`
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    # --- Locators ---
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def load(self):
        self.driver.get("https://example.com/login")

    def enter_username(self, username):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME_INPUT)).send_keys(username)

    def enter_password(self, password):
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)

    def click_login(self):
        self.driver.find_element(*self.LOGIN_BUTTON).click()
```

`pages/dashboard_page.py`
```python
from selenium.webdriver.common.by import By

class DashboardPage:
    # --- Locators ---
    HEADER = (By.TAG_NAME, "h1")

    def __init__(self, driver):
        self.driver = driver

    def get_header_text(self):
        return self.driver.find_element(*self.HEADER).text
```

### Test (`tests/test_login.py`)
```python
import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    yield driver
    driver.quit()

def test_successful_login(driver):
    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)

    # --- Test Steps ---
    login_page.load()
    login_page.enter_username("testuser")
    login_page.enter_password("password123")
    login_page.click_login()

    # --- Assertions ---
    assert "Dashboard" in driver.title
    assert dashboard_page.get_header_text() == "Welcome, testuser!"
```

### Selenium Best Practices
- **Use Explicit Waits**: `WebDriverWait` + `expected_conditions` provide reliable synchronization.
- **Adopt the Page Object Model**: Keeps locators and interactions separate from test logic.
- **Run Headless in CI**: Use `--headless` for CI/CD efficiency.

---

## 💾 19. Database Migration (Flyway)

Manage database schema evolution with version-controlled migrations and zero-downtime strategies.

### Configuration (`flyway.conf`)
```properties
# Database connection details
flyway.url=jdbc:postgresql://localhost:5432/myapp_db
flyway.user=myapp_user
flyway.password=supersecret
flyway.locations=filesystem:./migrations

# Schema to use
flyway.schemas=public
```

### Baseline Migration (`migrations/V1__Create_users_table.sql`)
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Schema Evolution (`migrations/V2__Add_full_name_to_users.sql`)
```sql
-- Add a new column to store the full name for better query performance
ALTER TABLE users ADD COLUMN full_name VARCHAR(101);

-- Note: We make it nullable first to avoid locking the table during the update.
-- The data backfill will be handled by an application script or a subsequent migration.
```

### Repeatable Migration (`migrations/R__Seed_admin_user.sql`)
```sql
INSERT INTO users (username, email, first_name, last_name)
VALUES ('admin', 'admin@example.com', 'Admin', 'User')
ON CONFLICT (username) DO NOTHING;
```

### Common Commands
```bash
# Check the status of migrations
flyway info

# Apply pending migrations to the database
flyway migrate

# Validate migration scripts against applied migrations
flyway validate
```

### Zero-Downtime Pattern
1. **Add New Column (Nullable)** — Fast metadata change; avoid table locks.
2. **Deploy Code (Dual Write)** — Application writes to old + new columns.
3. **Backfill Data** — Populate historical rows, ideally in batches.
4. **Deploy Code (Read from New)** — Switch reads/writes to the new column.
5. **Enforce NOT NULL** — Solidify data integrity guarantees.
6. **Drop Old Columns** — Clean up after monitoring for stability.

---

## 🌐 6. Terraform Multi-Cloud Deployment

Defines infrastructure across AWS, Azure, and GCP with a single Terraform configuration.

### Provider Configuration (`providers.tf`)
```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Remote state backend to securely store the state file
  backend "s3" {
    bucket = "my-terraform-state-bucket-unique" # CHANGE THIS
    key    = "multi-cloud/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

provider "azurerm" {
  features {}
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}
```

### Core Resources (`main.tf`)
```hcl
# --- AWS Resources ---
resource "aws_s3_bucket" "app_data" {
  bucket = "myapp-data-bucket-${random_id.id.hex}"
}

# --- Azure Resources ---
resource "azurerm_resource_group" "rg" {
  name     = "myapp-resources"
  location = var.azure_location
}

resource "azurerm_storage_account" "storage" {
  name                     = "myappstorage${random_id.id.hex}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# --- GCP Resources ---
resource "google_storage_bucket" "bucket" {
  name          = "myapp-gcp-bucket-${random_id.id.hex}"
  location      = "US"
  force_destroy = true
}

# --- Utility to ensure unique resource names ---
resource "random_id" "id" {
  byte_length = 8
}
```

### Terraform Commands
```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply "tfplan"
terraform state list
terraform destroy
```

---

## ☸️ 7. Kubernetes Deployment & Management

Deploys a containerized application to Kubernetes using declarative manifests.

### Deployment (`deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp-container
        image: myusername/my-app:latest # Replace with your image
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "250m"
            memory: "256Mi"
```

### Service (`service.yaml`)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  type: LoadBalancer # Exposes the service externally using a cloud provider's load balancer
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80       # Port exposed on the load balancer
      targetPort: 8080 # Port the container is listening on
```

### Essential `kubectl` Commands
```bash
kubectl apply -f deployment.yaml -f service.yaml
kubectl get deployment myapp-deployment
kubectl get pods -l app=myapp -o wide
kubectl get service myapp-service
POD_NAME=$(kubectl get pods -l app=myapp -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME
kubectl describe pod $POD_NAME
kubectl exec -it $POD_NAME -- /bin/sh
```

---

## 🐳 8. Container Orchestration with Docker Compose

Defines a multi-container application for local development, mirroring production-like setups.

### Compose File (`docker-compose.yml`)
```yaml
version: '3.9'

services:
  # --- Frontend Web Server ---
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf # Mount Nginx config
      - ./frontend:/usr/share/nginx/html            # Mount frontend code
    depends_on:
      - api

  # --- Backend API Service ---
  api:
    build: ./api # Build the image from the 'api' directory Dockerfile
    environment:
      - REDIS_HOST=redis
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
    depends_on:
      - redis
      - db
    networks:
      - app-network

  # --- Redis Caching Service ---
  redis:
    image: "redis:alpine"
    networks:
      - app-network

  # --- PostgreSQL Database ---
  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

# --- Networks and Volumes ---
networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
```

### Docker Compose Commands
```bash
docker-compose up -d --build
docker-compose down -v
docker-compose logs -f
docker-compose logs -f api
docker-compose exec api /bin/sh
docker-compose ps
```
