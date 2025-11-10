# AWS Kuiper Learning Path for System & Network Administrators

**From Zero AWS Experience to Functional Kuiper Sys/NetAdmin**

**Duration:** 12-16 weeks
**Role Focus:** System & Network Administrator for AWS Project Kuiper
**Prerequisites:** Basic networking knowledge, Linux familiarity

---

## Table of Contents

1. [Overview](#overview)
2. [Learning Path Structure](#learning-path-structure)
3. [Weeks 1-2: Foundation & Quick Start](#weeks-1-2-foundation--quick-start)
4. [Weeks 3-4: AWS Networking Fundamentals](#weeks-3-4-aws-networking-fundamentals)
5. [Weeks 5-6: Advanced Connectivity](#weeks-5-6-advanced-connectivity)
6. [Weeks 7-8: Kuiper-Specific Concepts](#weeks-7-8-kuiper-specific-concepts)
7. [Weeks 9-10: Observability & Automation](#weeks-9-10-observability--automation)
8. [Weeks 11-12: Security & Operations](#weeks-11-12-security--operations)
9. [Weeks 13-16: Advanced Topics & Certification](#weeks-13-16-advanced-topics--certification)
10. [Video Resources](#video-resources)
11. [Hands-On Labs](#hands-on-labs)
12. [Success Metrics](#success-metrics)

---

## Overview

### What is AWS Project Kuiper?

**AWS Project Kuiper** is Amazon's Low Earth Orbit (LEO) satellite constellation designed to provide high-speed broadband internet access globally. The system consists of:

- **~3,236 satellites** in LEO (Low Earth Orbit, ~590-630 km altitude)
- **Ground gateway stations** (POPs - Points of Presence)
- **Customer terminals** (user equipment)
- **AWS cloud integration** for control plane and services

### System & Network Administrator Role

As a Kuiper Sys/NetAdmin, you'll be responsible for:

1. **Ground Infrastructure Operations**
   - Gateway POP management and monitoring
   - Network connectivity (BGP/VPN/Direct Connect)
   - Multi-site redundancy and failover

2. **Cloud Edge Connectivity**
   - AWS Transit Gateway configuration
   - VPN tunnels with BGP routing
   - Direct Connect setup and management

3. **Security & Compliance**
   - PKI/mTLS implementation
   - IAM policies and least privilege
   - Audit logging and compliance

4. **Observability & Automation**
   - Monitoring dashboards (CloudWatch, Prometheus, Grafana)
   - Alert management (Alertmanager)
   - Infrastructure as Code (Terraform)
   - Configuration automation (Ansible)

5. **Incident Response & SRE**
   - On-call rotation
   - Runbook creation and maintenance
   - Blameless postmortems
   - SLO/SLI tracking

---

## Learning Path Structure

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Understand AWS basics and create your first resources

### Phase 2: Networking Core (Weeks 3-4)
**Goal:** Master VPCs, subnets, routing, and security groups

### Phase 3: Advanced Connectivity (Weeks 5-6)
**Goal:** Learn Transit Gateway, VPN, Direct Connect, and BGP

### Phase 4: Kuiper Specifics (Weeks 7-8)
**Goal:** Understand satellite networking and ground gateway operations

### Phase 5: Observability (Weeks 9-10)
**Goal:** Implement monitoring, logging, and alerting

### Phase 6: Security & Operations (Weeks 11-12)
**Goal:** Master PKI, IAM, automation, and runbooks

### Phase 7: Advanced & Certification (Weeks 13-16)
**Goal:** Deep dive into advanced topics and prepare for AWS certifications

---

## Weeks 1-2: Foundation & Quick Start

### Week 1: AWS Fundamentals

#### Day 1: AWS Account Setup & Navigation
**Time: 4 hours**

**Morning (2 hours): Account Creation**
- [ ] Create AWS account
- [ ] Enable MFA (Multi-Factor Authentication)
- [ ] Create IAM admin user (don't use root!)
- [ ] Install AWS CLI
- [ ] Configure AWS CLI with credentials
- [ ] Set up billing alerts

**Feynman Explanation:**
Think of AWS as a massive data center you can rent. Your "account" is like getting keys to use their computers, storage, and network equipment. MFA (Multi-Factor Authentication) is like having both a key AND a fingerprint scanner - two layers of security. IAM (Identity and Access Management) is the system that decides who can do what, like a building security badge system.

**Hands-On Lab:**
```bash
# Install AWS CLI (Linux/Mac)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
# Enter Access Key ID, Secret Access Key, default region (us-east-1), output format (json)

# Test configuration
aws sts get-caller-identity
```

**Afternoon (2 hours): Core Concepts**
- [ ] Study AWS Global Infrastructure (Regions, Availability Zones)
- [ ] Learn about AWS services landscape
- [ ] Understand the AWS Shared Responsibility Model
- [ ] Review AWS pricing basics

**Key Terms:**
- **Region:** Geographic area with multiple data centers (e.g., us-east-1 = Northern Virginia)
- **Availability Zone (AZ):** Isolated data center within a region (e.g., us-east-1a, us-east-1b)
- **VPC (Virtual Private Cloud):** Your private network in AWS
- **EC2 (Elastic Compute Cloud):** Virtual servers
- **S3 (Simple Storage Service):** Object storage

**Videos to Watch:**
- AWS Cloud Practitioner Essentials (AWS Training) - Module 1
- AWS Global Infrastructure Overview - AWS re:Invent Talk

**Resources:**
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [AWS Regions and AZs](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/)

---

#### Day 2: VPC Basics
**Time: 4 hours**

**Morning (2 hours): Understanding VPCs**

**Feynman Explanation:**
A VPC (Virtual Private Cloud) is like your own private data center network in the cloud. Imagine you're setting up a small office building:
- The **VPC** is the entire building
- **Subnets** are floors or rooms
- **Route tables** are the directions to get from one room to another
- **Internet Gateway** is the main entrance/exit
- **Security Groups** are like security guards checking IDs

**Core VPC Components:**
1. **CIDR Block:** Your IP address range (e.g., 10.0.0.0/16 gives you 65,536 IPs)
2. **Subnets:** Subdivisions of your VPC in specific AZs
3. **Route Tables:** Rules for directing network traffic
4. **Internet Gateway (IGW):** Door to the internet
5. **NAT Gateway:** Allows private subnets to reach internet (one-way)

**Hands-On Lab: Create Your First VPC**
```bash
# Via AWS CLI
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyFirstVPC}]'

# Create public subnet
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# Create internet gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id <vpc-id> --internet-gateway-id <igw-id>
```

**Afternoon (2 hours): Subnets & Routing**
- [ ] Create public and private subnets
- [ ] Configure route tables
- [ ] Attach Internet Gateway
- [ ] Understand public vs private subnets

**Visual Exercise:** Draw your VPC architecture on paper
```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24) - AZ-1a
│   └── Route: 0.0.0.0/0 → Internet Gateway
├── Private Subnet (10.0.2.0/24) - AZ-1a
│   └── Route: 0.0.0.0/0 → NAT Gateway
├── Public Subnet (10.0.3.0/24) - AZ-1b
└── Private Subnet (10.0.4.0/24) - AZ-1b
```

**Key Concepts:**
- **Public Subnet:** Has route to Internet Gateway (0.0.0.0/0 → IGW)
- **Private Subnet:** No direct internet access; uses NAT Gateway for outbound
- **Multi-AZ:** Distribute subnets across multiple AZs for high availability

**Videos:**
- AWS VPC Beginner's Guide (Stephane Maarek)
- VPC with Public and Private Subnets (AWS Tutorial)

**Resources:**
- [VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [VPC Design Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-design.html)

---

#### Day 3: Security Groups & NACLs
**Time: 4 hours**

**Morning (2 hours): Security Groups**

**Feynman Explanation:**
Security Groups are like bouncers at a club. They check every person (network packet) trying to enter or leave:
- **Inbound rules:** Who can come IN (e.g., "Allow web traffic from anywhere")
- **Outbound rules:** Where you can go OUT (default: allow all)
- **Stateful:** If you let someone in, they can automatically leave (return traffic allowed)

**Security Group Rules Structure:**
```
Type     | Protocol | Port Range | Source/Destination
SSH      | TCP      | 22         | 203.0.113.0/24
HTTP     | TCP      | 80         | 0.0.0.0/0
HTTPS    | TCP      | 443        | 0.0.0.0/0
Custom   | TCP      | 8080       | sg-12345678 (another security group)
```

**Hands-On Lab:**
```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-servers \
  --description "Security group for web servers" \
  --vpc-id <vpc-id>

# Add inbound rule for SSH
aws ec2 authorize-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Add inbound rule for HTTPS
aws ec2 authorize-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

**Afternoon (2 hours): NACLs and Comparison**

**Network ACLs (NACLs) - Feynman Explanation:**
NACLs are like checkpoint guards at the subnet level - they check EVERY car (packet) entering or leaving the entire neighborhood (subnet), not just individual houses. Unlike Security Groups (stateful), NACLs are **stateless** - you must explicitly allow BOTH inbound AND outbound traffic.

**Key Differences:**

| Feature | Security Group | NACL |
|---------|---------------|------|
| **Level** | Instance (EC2) | Subnet |
| **State** | Stateful (return traffic automatic) | Stateless (must allow both ways) |
| **Rules** | Allow only | Allow AND Deny |
| **Evaluation** | All rules | Rules in order (lowest number first) |
| **Default** | Deny all inbound, allow all outbound | Allow all |

**When to Use What:**
- **Security Groups:** 99% of the time for instance-level security
- **NACLs:** Extra layer for subnet-level blocking (e.g., block entire IP ranges)

**Best Practice:** Use Security Groups as primary, NACLs as backup/subnet-wide controls

**Videos:**
- AWS Security Groups vs NACLs (Digital Cloud Training)
- VPC Security Deep Dive (AWS re:Invent)

---

#### Day 4: EC2 Launch & Connect
**Time: 4 hours**

**Morning (2 hours): Launch First EC2 Instance**

**Feynman Explanation:**
EC2 (Elastic Compute Cloud) is renting a computer in AWS's data center. You choose:
1. **Instance Type:** How powerful (t2.micro = small laptop, m5.large = gaming PC)
2. **AMI (Amazon Machine Image):** What's already installed (like choosing Windows vs Linux)
3. **Network:** Which VPC/subnet (which building/floor)
4. **Storage:** How much disk space (EBS = Elastic Block Store)
5. **Key Pair:** Your SSH key (like your house key to log in)

**Hands-On Lab: Launch EC2**

Via AWS Console:
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose Amazon Linux 2 AMI (free tier)
4. Select t2.micro instance type
5. Configure:
   - Network: Your VPC
   - Subnet: Public subnet
   - Auto-assign Public IP: Enable
6. Add 8 GB storage (default)
7. Create/select key pair
8. Configure Security Group (allow SSH from your IP)
9. Launch!

Via CLI:
```bash
# Create key pair
aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
chmod 400 my-key.pem

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --count 1 \
  --instance-type t2.micro \
  --key-name my-key \
  --security-group-ids <sg-id> \
  --subnet-id <subnet-id>
```

**Afternoon (2 hours): Connect & Explore**

**SSH Connection:**
```bash
# Get public IP
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].PublicIpAddress'

# Connect via SSH
ssh -i my-key.pem ec2-user@<public-ip>

# Once connected, explore:
whoami
uname -a
df -h
free -m
ip addr show
```

**Install Basic Tools:**
```bash
sudo yum update -y
sudo yum install -y htop tree net-tools tcpdump
```

**Key Concepts:**
- **AMI:** Pre-configured OS image
- **Instance Type:** CPU/RAM/Network specs (t2.micro = 1 vCPU, 1 GB RAM)
- **EBS:** Block storage attached to instances
- **Key Pair:** RSA key for SSH authentication
- **User Data:** Script that runs on first boot

**Videos:**
- Launching Your First EC2 Instance (AWS Tutorial)
- EC2 Instance Types Explained (A Cloud Guru)

---

#### Day 5: Review & Practice
**Time: 4 hours**

**Morning (2 hours): Build From Scratch**

**Challenge:** Build this architecture without looking at notes:

```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24) - us-east-1a
│   ├── Internet Gateway attached
│   ├── Route: 0.0.0.0/0 → IGW
│   └── Web Server EC2 (port 80 open to world)
│
└── Private Subnet (10.0.2.0/24) - us-east-1a
    ├── NAT Gateway (in public subnet)
    ├── Route: 0.0.0.0/0 → NAT
    └── Database EC2 (port 3306 only from web server)
```

**Steps:**
1. Create VPC
2. Create subnets (public + private)
3. Create & attach Internet Gateway
4. Create NAT Gateway (place in public subnet)
5. Configure route tables
6. Create security groups (web-tier, db-tier)
7. Launch EC2 instances
8. Test connectivity

**Afternoon (2 hours): Troubleshooting Practice**

**Common Issues & Fixes:**

1. **Can't SSH to EC2**
   - Check: Security group allows port 22 from your IP
   - Check: Instance in public subnet with IGW route
   - Check: Correct key file (`chmod 400 my-key.pem`)
   - Check: Using correct username (ec2-user, ubuntu, admin)

2. **EC2 can't reach internet**
   - Public subnet: Check IGW attachment and route
   - Private subnet: Check NAT Gateway and route

3. **Can't ping between instances**
   - Security groups must allow ICMP (ping)
   - Check source/destination in rules

**Troubleshooting Commands:**
```bash
# From your laptop
ssh -vvv -i my-key.pem ec2-user@<ip>  # Verbose SSH
telnet <ip> 22  # Test if port 22 open

# From EC2 instance
ping 8.8.8.8  # Test internet
curl ifconfig.me  # Get public IP
sudo tcpdump -i eth0  # Watch network traffic
netstat -tulpn  # Show listening ports
```

**Videos:**
- AWS VPC Troubleshooting (Linux Academy)
- EC2 Connectivity Issues (AWS Support)

---

### Week 2: AWS Services & Networking Deep Dive

#### Day 6: Route 53 (DNS)
**Time: 4 hours**

**Morning (2 hours): DNS Basics & Route 53**

**Feynman Explanation:**
DNS (Domain Name System) is like the internet's phone book. When you type "google.com", DNS translates it to an IP address (like 142.250.185.46). Route 53 is AWS's DNS service - it's called "53" because DNS uses port 53.

**Route 53 Core Concepts:**

1. **Hosted Zone:** Container for DNS records for a domain
   - **Public Hosted Zone:** Internet-facing (example.com)
   - **Private Hosted Zone:** Only accessible from your VPCs

2. **DNS Record Types:**
   - **A Record:** Domain → IPv4 (example.com → 1.2.3.4)
   - **AAAA Record:** Domain → IPv6
   - **CNAME:** Alias (www.example.com → example.com)
   - **Alias Record:** AWS-specific, free (example.com → ELB)
   - **MX:** Mail servers
   - **TXT:** Text records (often for verification)

3. **Routing Policies:**
   - **Simple:** One record, one or more IPs (random selection)
   - **Weighted:** Distribute traffic by percentage (80% to A, 20% to B)
   - **Latency:** Send user to closest region
   - **Geolocation:** Route based on user's location (EU → eu-west-1)
   - **Failover:** Primary/secondary with health checks
   - **Multivalue:** Like simple but with health checks

**Hands-On Lab:**
```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference $(date +%s)

# Create A record
cat > change-batch.json << EOF
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "www.example.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "1.2.3.4"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch file://change-batch.json
```

**Afternoon (2 hours): Health Checks & Failover**

**Health Checks - Feynman Explanation:**
Imagine Route 53 as a traffic cop directing cars (users). Health checks are like the cop calling ahead to make sure the destination is open before sending anyone there. If the destination is down (health check fails), the cop redirects traffic to a backup location.

**Health Check Types:**
1. **Endpoint:** Monitor a specific URL (http://api.example.com/health)
2. **Calculated:** Combine multiple health checks (AND/OR logic)
3. **CloudWatch Alarm:** Based on CloudWatch metrics

**Failover Setup:**
```
Primary Record (us-east-1) → Health Check → If healthy: use
   ↓ (if unhealthy)
Secondary Record (us-west-2) → Always use if primary fails
```

**Hands-On: Failover Configuration**
1. Create two EC2 instances in different regions
2. Create health checks for each
3. Create Route 53 records with failover policy
4. Test by stopping primary instance

**Key Concepts:**
- **TTL (Time To Live):** How long DNS answer is cached (300 seconds = 5 minutes)
- **Lower TTL:** Faster failover, more DNS queries (higher cost)
- **Health Check Interval:** How often to check (30 seconds standard, 10 seconds fast)

**Videos:**
- Route 53 Deep Dive (AWS re:Invent)
- DNS Failover with Route 53 (AWS Tutorial)

**Resources:**
- [Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [Routing Policies Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)

---

#### Day 7: Load Balancers (ELB/ALB/NLB)
**Time: 4 hours**

**Morning (2 hours): Load Balancer Types**

**Feynman Explanation:**
A load balancer is like a restaurant host distributing customers across multiple servers (waiters). Instead of everyone lining up at one waiter, the host spreads people out so everyone gets served faster. If one waiter is overwhelmed or goes on break, the host stops sending them customers.

**AWS Load Balancer Types:**

1. **Application Load Balancer (ALB) - Layer 7 (HTTP/HTTPS)**
   - Routes based on URL path, hostname, headers
   - Best for: Web applications, microservices, containers
   - Example: /api/users → Backend 1, /api/orders → Backend 2

2. **Network Load Balancer (NLB) - Layer 4 (TCP/UDP)**
   - Ultra-high performance, low latency
   - Preserves source IP
   - Best for: Non-HTTP protocols, extreme performance needs
   - Example: Database connections, gaming servers

3. **Classic Load Balancer (CLB) - Legacy**
   - Don't use for new projects
   - Being phased out

**ALB vs NLB Decision Matrix:**

| Use Case | Choose |
|----------|--------|
| HTTP/HTTPS web apps | ALB |
| Need path-based routing | ALB |
| Need host-based routing | ALB |
| TCP/UDP (non-HTTP) | NLB |
| Need static IP | NLB |
| Extreme performance (millions of requests/sec) | NLB |

**Hands-On Lab: Create ALB**

Via Console:
1. EC2 → Load Balancers → Create Load Balancer
2. Choose Application Load Balancer
3. Configure:
   - Name: my-alb
   - Scheme: Internet-facing
   - Availability Zones: Select 2+ AZs
4. Configure Security Group (allow HTTP 80, HTTPS 443)
5. Create Target Group:
   - Target type: Instances
   - Protocol: HTTP, Port: 80
   - Health check: /health
6. Register targets (your EC2 instances)
7. Review and create

**Afternoon (2 hours): Target Groups & Health Checks**

**Target Groups - Feynman Explanation:**
A target group is like a team of workers that can handle specific tasks. The load balancer sends work (requests) to the team, and the team distributes it among its members. If a member is sick (unhealthy), the team stops giving them work until they recover.

**Health Check Configuration:**
```json
{
  "HealthCheckProtocol": "HTTP",
  "HealthCheckPort": "80",
  "HealthCheckPath": "/health",
  "HealthCheckIntervalSeconds": 30,
  "HealthCheckTimeoutSeconds": 5,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3
}
```

**How Health Checks Work:**
1. LB sends request to `/health` every 30 seconds
2. Expects HTTP 200 response within 5 seconds
3. If 2 consecutive successes → mark healthy
4. If 3 consecutive failures → mark unhealthy (stop sending traffic)

**Health Check Endpoint Best Practices:**
```python
# Flask example
@app.route('/health')
def health_check():
    # Check database connection
    if not db.is_connected():
        return "Database unavailable", 503

    # Check critical services
    if not cache.is_connected():
        return "Cache unavailable", 503

    return "OK", 200
```

**Sticky Sessions (Session Affinity):**
- Ensures user stays on same instance
- Useful for: stateful applications, user sessions
- ALB uses cookie (AWSALB or application cookie)

**Videos:**
- ALB Deep Dive (AWS re:Invent)
- Choosing the Right Load Balancer (AWS)

---

#### Day 8: CloudWatch Monitoring
**Time: 4 hours**

**Morning (2 hours): CloudWatch Basics**

**Feynman Explanation:**
CloudWatch is like having security cameras and sensors throughout your AWS environment. It constantly watches and records what's happening (metrics), stores video footage (logs), and can alert security guards (you) when something unusual occurs (alarms).

**Core CloudWatch Components:**

1. **Metrics:** Numerical data points over time
   - EC2: CPUUtilization, NetworkIn/Out, DiskReadBytes
   - VPN: TunnelState, TunnelDataIn/Out
   - Custom: Your application metrics

2. **Logs:** Text logs from applications/services
   - Log Groups: Container for log streams (e.g., /aws/lambda/my-function)
   - Log Streams: Sequence of log events (e.g., one per Lambda execution)
   - Retention: How long to keep logs (1 day to never expire)

3. **Alarms:** Notifications when metrics cross thresholds
   - States: OK, ALARM, INSUFFICIENT_DATA
   - Actions: SNS notification, Auto Scaling, EC2 action

4. **Dashboards:** Visual representation of metrics

**Hands-On: Create Dashboard**

```bash
# Via CLI - Create dashboard JSON
cat > dashboard.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "EC2 CPU Utilization"
      }
    }
  ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name MyDashboard \
  --dashboard-body file://dashboard.json
```

**Afternoon (2 hours): Alarms & Notifications**

**Creating Alarms - Step by Step:**

1. **Choose Metric:** What to monitor (CPU, disk, custom)
2. **Set Conditions:** When to alarm
   - Static threshold: CPU > 80%
   - Anomaly detection: Unusual pattern
3. **Configure Actions:** What to do
   - Send SNS notification
   - Trigger Auto Scaling
   - Stop/terminate instance
4. **Test:** Manually trigger alarm

**Alarm Example: High CPU**
```bash
# Create SNS topic for notifications
aws sns create-topic --name high-cpu-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789:high-cpu-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --alarm-actions arn:aws:sns:us-east-1:123456789:high-cpu-alerts
```

**Alarm Best Practices:**
- Set 2-3 evaluation periods (avoid flapping)
- Use appropriate statistic (Average for CPU, Sum for errors)
- Test alarms regularly
- Document response procedures
- Use composite alarms for complex logic

**Videos:**
- CloudWatch Fundamentals (AWS Training)
- CloudWatch Alarms Deep Dive (AWS re:Invent)

---

#### Day 9: IAM (Identity & Access Management)
**Time: 4 hours**

**Morning (2 hours): IAM Concepts**

**Feynman Explanation:**
IAM is like an employee badge system for AWS. Different badges (roles/policies) give access to different rooms (services) and different permissions (read-only vs full access). You can create badges for humans (users), services (roles), and even other companies (federated access).

**IAM Core Components:**

1. **Users:** Actual people who need access
   - Username/password for Console
   - Access Key/Secret for CLI/API
   - Enable MFA for security

2. **Groups:** Collection of users (e.g., "Developers", "Admins")
   - Attach policies to groups
   - Users inherit group permissions

3. **Roles:** Identity that services can assume
   - No long-term credentials
   - Used by: EC2, Lambda, ECS, other accounts
   - Example: EC2 instance role to access S3

4. **Policies:** JSON documents defining permissions
   - **Managed Policies:** AWS-created or reusable
   - **Inline Policies:** Attached directly to specific user/role
   - Format: Effect (Allow/Deny), Action, Resource

**Policy Structure:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    },
    {
      "Sid": "DenyS3Delete",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "*"
    }
  ]
}
```

**Hands-On: Create IAM Role for EC2**

```bash
# Create trust policy (who can assume the role)
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name EC2-S3-ReadOnly \
  --assume-role-policy-document file://trust-policy.json

# Attach AWS managed policy
aws iam attach-role-policy \
  --role-name EC2-S3-ReadOnly \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create instance profile (wrapper for role)
aws iam create-instance-profile --instance-profile-name EC2-S3-ReadOnly
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-S3-ReadOnly \
  --role-name EC2-S3-ReadOnly

# Attach to EC2
aws ec2 associate-iam-instance-profile \
  --instance-id i-1234567890abcdef0 \
  --iam-instance-profile Name=EC2-S3-ReadOnly
```

**Afternoon (2 hours): Least Privilege & Best Practices**

**Least Privilege Principle:**
Only give the minimum permissions needed to do the job. Example:

**Bad (too broad):**
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}
```

**Good (specific):**
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject"
  ],
  "Resource": "arn:aws:s3:::my-app-bucket/uploads/*"
}
```

**IAM Best Practices:**

1. **Use Roles, Not Users:**
   - EC2 → IAM Role (not hardcoded keys)
   - Lambda → IAM Role
   - Cross-account → IAM Role

2. **Enable MFA:**
   - Require MFA for privileged operations
   - Use virtual MFA (Google Authenticator, Authy)

3. **Rotate Credentials:**
   - Rotate access keys every 90 days
   - Use IAM Credential Report to audit

4. **Use Groups:**
   - Never attach policies directly to users
   - Create groups (Admins, Developers, ReadOnly)

5. **Monitor with CloudTrail:**
   - Log all API calls
   - Set up alarms for suspicious activity

**IAM Access Analyzer:**
Finds resources shared with external accounts:
```bash
# Create analyzer
aws accessanalyzer create-analyzer \
  --analyzer-name my-analyzer \
  --type ACCOUNT

# List findings
aws accessanalyzer list-findings --analyzer-arn <arn>
```

**Videos:**
- IAM Deep Dive (AWS re:Invent)
- IAM Best Practices (AWS Security)

**Resources:**
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM Policy Generator](https://awspolicygen.s3.amazonaws.com/policygen.html)

---

#### Day 10: Week 2 Review & Mini-Project
**Time: 6 hours**

**Morning (3 hours): Build Multi-Tier Architecture**

**Challenge:** Create this production-like setup:

```
Multi-AZ, Multi-Tier Web Application
=====================================

Region: us-east-1
VPC: 10.0.0.0/16

Public Subnets (ALB):
├── 10.0.1.0/24 (AZ-1a) → ALB Target
└── 10.0.2.0/24 (AZ-1b) → ALB Target

Private Subnets (Web Tier):
├── 10.0.11.0/24 (AZ-1a) → EC2 Instances
└── 10.0.12.0/24 (AZ-1b) → EC2 Instances

Private Subnets (Database Tier):
├── 10.0.21.0/24 (AZ-1a) → RDS Primary
└── 10.0.22.0/24 (AZ-1b) → RDS Standby

NAT Gateways:
├── NAT-1a in 10.0.1.0/24
└── NAT-1b in 10.0.2.0/24

Components:
- Application Load Balancer (public)
- 2x EC2 web servers (private, auto-scaled)
- RDS MySQL Multi-AZ (private)
- Route 53 DNS
- CloudWatch dashboards & alarms
- IAM roles (EC2 → RDS, EC2 → S3)
```

**Implementation Steps:**

1. **Create VPC Infrastructure (60 min)**
   - VPC with CIDR 10.0.0.0/16
   - 6 subnets across 2 AZs
   - Internet Gateway
   - 2 NAT Gateways (one per AZ)
   - Route tables configured

2. **Deploy Web Tier (60 min)**
   - Launch 2 EC2 instances (t2.micro, Amazon Linux 2)
   - Install Apache/Nginx
   - Configure Security Groups (allow ALB → EC2:80)
   - Create IAM role for EC2 → S3/CloudWatch

3. **Configure Load Balancer (30 min)**
   - Create ALB in public subnets
   - Create target group with health checks
   - Register EC2 instances
   - Configure Security Group (allow internet → ALB:80)

4. **Set Up DNS (15 min)**
   - Create Route 53 hosted zone
   - Create Alias record pointing to ALB

5. **Configure Monitoring (45 min)**
   - CloudWatch dashboard with:
     - ALB: RequestCount, TargetResponseTime, HTTPCode_Target_5XX
     - EC2: CPUUtilization, NetworkIn/Out
     - System metrics (disk, memory via CloudWatch Agent)
   - Create alarms:
     - ALB 5XX > 10 in 5 minutes
     - EC2 CPU > 80% for 10 minutes
   - SNS topic for notifications

**Afternoon (3 hours): Test, Break, Fix**

**Testing Scenarios:**

1. **Load Testing:**
```bash
# Install Apache Bench
sudo yum install httpd-tools -y

# Generate load
ab -n 10000 -c 100 http://your-alb-dns/
```

Watch CloudWatch metrics spike, verify:
- Load distributed across instances
- Health checks passing
- No 5XX errors

2. **Failure Simulation:**

**Scenario A: Instance Failure**
```bash
# Stop one EC2 instance
aws ec2 stop-instances --instance-ids <instance-id>

# Observe:
# - ALB marks instance unhealthy
# - Traffic shifts to remaining instance
# - CloudWatch alarm triggers (if configured)
# - Application remains accessible
```

**Scenario B: AZ Failure**
```bash
# Simulate by stopping all instances in one AZ
# Or modify NACL to block all traffic

# Observe:
# - ALB routes all traffic to healthy AZ
# - Application performance degrades (half capacity)
# - Alarms trigger
# - Application still accessible
```

**Scenario C: Security Misconfiguration**
```bash
# Remove HTTP rule from EC2 security group
aws ec2 revoke-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 80 \
  --source-group <alb-sg-id>

# Observe:
# - All health checks fail
# - ALB returns 502 (bad gateway)
# - Application inaccessible
```

**Troubleshooting Exercise:**

**Problem:** Application returns 502 errors

**Checklist:**
1. Check ALB target health:
   ```bash
   aws elbv2 describe-target-health --target-group-arn <arn>
   ```
2. Check EC2 instances running
3. Check Security Group (ALB → EC2)
4. Check NACL (subnet-level)
5. SSH to EC2, check application logs
6. Check application actually listening on port 80

**Problem:** Some requests timeout

**Checklist:**
1. Check CloudWatch: ResponseTime metric
2. Check EC2 CPU/Memory
3. Check database connections
4. Review application logs
5. Test health check endpoint directly

**Cleanup (IMPORTANT!):**
```bash
# To avoid charges, delete in order:
1. ALB
2. Target Group
3. EC2 Instances
4. NAT Gateways (charges per hour!)
5. Elastic IPs
6. RDS (if created)
7. VPC (will delete subnets, IGW, etc.)
```

**Week 2 Accomplishments:**
✅ Launched and managed EC2 instances
✅ Configured VPC networking
✅ Set up load balancing (ALB)
✅ Configured DNS (Route 53)
✅ Implemented monitoring (CloudWatch)
✅ Applied IAM best practices
✅ Built multi-tier, multi-AZ architecture
✅ Performed failure testing
✅ Learned troubleshooting methodologies

**Videos:**
- Building a Multi-Tier Architecture (AWS Workshop)
- High Availability Best Practices (AWS re:Invent)

---

## End of Weeks 1-2 Detailed Content

**Next Steps:**
- Complete Week 3-4 content will cover:
  - Transit Gateway in depth
  - Site-to-Site VPN with BGP
  - Direct Connect
  - Advanced routing scenarios
  - Multi-region connectivity

**Self-Assessment Questions:**
1. Can you explain VPC, subnet, route table, and security group to a non-technical person?
2. Can you create a VPC with public/private subnets from scratch?
3. Can you troubleshoot why an EC2 instance can't reach the internet?
4. Can you set up an ALB with health checks?
5. Can you create IAM roles and policies following least privilege?
6. Can you build a CloudWatch dashboard with alarms?

**Certification Path:**
After weeks 1-2, you're ready to start studying for:
- AWS Certified Cloud Practitioner (foundation)
- AWS Certified Solutions Architect Associate (next goal)

---

**Continue to:** [Weeks 3-4: AWS Networking Fundamentals](#weeks-3-4-aws-networking-fundamentals)
