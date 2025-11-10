# Complete Enterprise Portfolio - Code Examples Index

**Last Updated:** November 10, 2025
**Status:** ✅ Complete
**Total Lines of Code:** 2,500+

This comprehensive index provides a navigable overview of all enterprise-level code examples organized by engineering role. Each section demonstrates production-ready implementations with best practices, security hardening, and scalability considerations.

---

## 📑 Quick Navigation

- [System Development Engineer](#system-development-engineer)
- [DevOps Engineer](#devops-engineer)
- [QA Engineer III](#qa-engineer)
- [Solutions Architect](#solutions-architect)
- [Technology Stack](#technology-stack)
- [Key Metrics](#key-metrics)

---

## <a id="system-development-engineer"></a> 🔧 System Development Engineer

### Infrastructure as Code - Terraform Modules

Complete AWS infrastructure provisioning with modular, reusable components.

#### 1. VPC Network Infrastructure

**Location:** [`terraform/modules/vpc/`](terraform/modules/vpc/)

**Files:**
- `main.tf` - 187 lines | VPC, subnets, NAT gateways, flow logs
- `variables.tf` - Configuration parameters
- `outputs.tf` - Exported values

**Features:**
- Multi-AZ deployment (1-3 availability zones)
- Three-tier architecture (public/private/database subnets)
- NAT Gateways with high availability
- VPC Flow Logs for security monitoring
- S3 VPC Endpoint for private access

**Resources Created:** 15+ AWS resources
**Monthly Cost:** $45-135 (varies by NAT Gateway count)

**Usage Example:**
```hcl
module "vpc" {
  source             = "./modules/vpc"
  environment        = "production"
  vpc_cidr          = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
}
```

---

#### 2. EKS Kubernetes Cluster

**Location:** [`terraform/modules/eks/`](terraform/modules/eks/)

**Files:**
- `main.tf` - 237 lines | Cluster, node groups, OIDC provider
- `variables.tf` - Cluster configuration
- `outputs.tf` - Cluster details
- `user_data.sh` - Node bootstrap script

**Features:**
- EKS 1.28+ with managed node groups
- KMS encryption for Kubernetes secrets
- OIDC provider for IAM Roles for Service Accounts (IRSA)
- Auto-scaling node groups (configurable min/max)
- CloudWatch logging for all control plane components
- Multi-AZ node distribution
- Security group rules with least privilege

**Resources Created:** 20+ AWS resources
**Monthly Cost:** $220-800 (varies by node count/type)

**Usage Example:**
```hcl
module "eks" {
  source                = "./modules/eks"
  environment           = "production"
  vpc_id               = module.vpc.vpc_id
  subnet_ids           = module.vpc.public_subnet_ids
  private_subnet_ids   = module.vpc.private_subnet_ids
  kubernetes_version   = "1.28"
  desired_size         = 3
  min_size            = 2
  max_size            = 10
}
```

---

#### 3. RDS PostgreSQL Database

**Location:** [`terraform/modules/rds/`](terraform/modules/rds/)

**Files:**
- `main.tf` - 215 lines | RDS instance, parameter group, monitoring
- `variables.tf` - Database settings
- `outputs.tf` - Connection details

**Features:**
- PostgreSQL 15.4 with Multi-AZ deployment
- Storage encryption with customer-managed KMS keys
- Automated backups (30-day retention for production)
- Performance Insights enabled
- Read replica support (optional)
- CloudWatch alarms (CPU, storage, connections)
- Secrets Manager integration for credentials
- Custom parameter group with logging enabled

**Resources Created:** 10+ AWS resources
**Monthly Cost:** $180-450 (depends on instance class)

**Usage Example:**
```hcl
module "rds" {
  source                  = "./modules/rds"
  environment             = "production"
  vpc_id                 = module.vpc.vpc_id
  subnet_ids             = module.vpc.database_subnet_ids
  instance_class         = "db.r6g.large"
  allocated_storage      = 100
  create_replica         = true
  allowed_security_groups = [module.eks.cluster_security_group_id]
}
```

---

#### 4. Main Infrastructure Orchestration

**Location:** [`terraform/main.tf`](terraform/main.tf)

**Features:**
- S3 backend for state management
- DynamoDB state locking
- Multi-region provider support
- Default tags for all resources
- Environment-based configuration

**Usage:**
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

---

## <a id="devops-engineer"></a> 🚀 DevOps Engineer

### CI/CD Pipeline Architecture

#### 1. GitHub Actions Production Pipeline

**Location:** [`cicd/github-actions/production.yml`](cicd/github-actions/production.yml)

**Pipeline Stages:** 8 comprehensive stages

**378 lines of production-ready CI/CD automation**

##### Stage 1: Code Quality & Security
- ESLint, Prettier, TypeScript type checking
- npm audit for dependency vulnerabilities
- Semgrep SAST security scanning
- Snyk dependency vulnerability scanning

##### Stage 2: Unit Tests
- Multi-version testing (Node.js 18.x, 20.x)
- Code coverage reporting (Codecov)
- SonarCloud quality analysis
- 80%+ coverage requirement

##### Stage 3: Integration Tests
- PostgreSQL 15 service container
- Redis 7 service container
- Database migration validation
- Service integration verification

##### Stage 4: End-to-End Tests
- Playwright browser testing
- Complete user journey validation
- Test report artifacts
- Screenshot capture on failure

##### Stage 5: Build & Push Docker Images
- Multi-architecture builds (amd64, arm64)
- Docker Buildx with caching
- Trivy container vulnerability scanning
- SBOM (Software Bill of Materials) generation
- GitHub Container Registry (ghcr.io) push

##### Stage 6: Deploy to Staging
- AWS EKS deployment
- Helm chart installation
- Smoke test execution
- Rollout status verification
- Slack notifications

##### Stage 7: Performance Testing
- K6 load testing
- Performance metrics collection
- Threshold validation
- Results artifact upload

##### Stage 8: Deploy to Production
- Deployment backup creation
- Canary deployment (10% traffic)
- Metrics monitoring (5-minute observation)
- Full rollout on success
- Deployment tracker update
- Team notifications

**Pipeline Duration:** 15-25 minutes (full run)
**Success Rate Target:** >95%
**Deployment Frequency:** Multiple times per day

---

#### 2. GitOps with ArgoCD

**Location:** [`cicd/argocd/portfolio-prod.yaml`](cicd/argocd/portfolio-prod.yaml)

**Features:**
- Automated sync policy with self-healing
- Prune propagation for clean updates
- Rollback capabilities (10 revisions)
- Kustomize integration for environment-specific configs
- RBAC with admin and developer roles
- Notification integrations:
  - Slack for deployment success
  - PagerDuty for health degradation

**120 lines of declarative GitOps configuration**

**Sync Strategy:**
- Automated pruning of removed resources
- Self-healing on configuration drift
- 5 retry attempts with exponential backoff
- Respect ignore differences for dynamic fields

---

### Kubernetes Manifests

#### 3. Production-Ready K8s Resources

**Location:** [`cicd/k8s/base/deployment.yaml`](cicd/k8s/base/deployment.yaml)

**267 lines of hardened Kubernetes manifests**

**Includes:**

##### Deployment
- 3 replicas with rolling update strategy
- Security context (non-root, read-only filesystem)
- Resource requests/limits
- Init container for database readiness
- Health probes (liveness, readiness, startup)
- Pod anti-affinity for high availability

##### Service
- ClusterIP type for internal communication
- Port 80 → 8080 mapping

##### Ingress
- NGINX ingress controller
- SSL/TLS with cert-manager
- Rate limiting (100 req/min, 10 req/s)
- Force SSL redirect

##### HorizontalPodAutoscaler (HPA)
- 3-10 replica range
- CPU target: 70% utilization
- Memory target: 80% utilization
- Scale-down stabilization: 5 minutes
- Scale-up policies: 100% increase or 2 pods/60s

##### PodDisruptionBudget (PDB)
- Minimum 2 available pods
- Protects against voluntary disruptions

##### NetworkPolicy
- Ingress from NGINX and Prometheus only
- Egress to database, cache, DNS, HTTPS
- Default deny for other traffic

**Security Hardening:**
- Non-root containers (UID 1000)
- Read-only root filesystem
- No privilege escalation
- All capabilities dropped
- Security context at pod and container level

---

## <a id="qa-engineer"></a> 🧪 QA Engineer III

### Testing Framework Examples

#### 1. Jest Unit Tests

**Location:** [`tests/unit/services/user.service.test.ts`](tests/unit/services/user.service.test.ts)

**201 lines of comprehensive unit tests**

**Test Coverage:**
- User creation with validation
- Authentication flows (login, JWT)
- Password hashing and verification
- Email verification
- User updates and deletes
- Error handling scenarios
- Mock implementations for dependencies

**Test Scenarios:**
- ✅ Create user with valid data
- ✅ Validate email format
- ✅ Validate password strength
- ✅ Handle duplicate email conflicts
- ✅ Authenticate with valid credentials
- ✅ Reject invalid credentials
- ✅ Verify email requirement
- ✅ Update user profile
- ✅ Soft delete users

**Run Command:**
```bash
npm run test:unit -- --coverage
```

**Coverage Target:** >80%

---

#### 2. Cypress End-to-End Tests

**Location:** [`tests/e2e/user-authentication.cy.ts`](tests/e2e/user-authentication.cy.ts)

**154+ lines of E2E automation**

**Test Suites:**

##### User Registration Flow
- Successful registration with valid data
- Validation error display for invalid input
- Prevention of duplicate email registration

##### User Login Flow
- Login with valid credentials
- Error handling for invalid credentials
- Rate limiting protection (5 failed attempts)

##### Password Reset Flow
- Initiate password reset request
- Reset password with valid token
- Email verification

##### Session Management
- Session persistence across page reloads
- Successful logout
- Redirect to login on session expiration

**Run Command:**
```bash
npx cypress run
```

**Browser Support:** Chrome, Firefox, Edge

---

#### 3. Playwright API Tests

**Location:** [`tests/api/user-api.test.ts`](tests/api/user-api.test.ts)

**89 lines of API contract testing**

**Test Coverage:**
- RESTful API endpoint validation
- Authentication with Bearer tokens
- CRUD operations (Create, Read, Update, Delete)
- HTTP status code verification
- Response payload validation
- Error response handling
- Unauthorized access prevention

**Test Scenarios:**
- ✅ GET /users/:id returns user data
- ✅ PUT /users/:id updates user
- ✅ GET without auth returns 401
- ✅ POST with invalid data returns 400

**Run Command:**
```bash
npx playwright test
```

---

#### 4. K6 Performance Tests

**Location:** [`tests/performance/load-test.js`](tests/performance/load-test.js)

**176 lines of load testing**

**Load Test Configuration:**

**Stages:**
1. Ramp-up to 50 users (2 minutes)
2. Sustain 50 users (5 minutes)
3. Ramp-up to 100 users (2 minutes)
4. Sustain 100 users (5 minutes)
5. Ramp-up to 200 users (2 minutes)
6. Sustain 200 users (5 minutes)
7. Ramp-down to 0 (5 minutes)

**Total Duration:** 27 minutes

**Thresholds:**
- p95 response time < 500ms
- p99 response time < 1000ms
- Error rate < 1%

**Test Scenarios:**
1. User login
2. Product browsing
3. Search queries
4. Profile viewing

**Custom Metrics:**
- Error rate tracking
- Response time trends
- Request counters

**Run Command:**
```bash
k6 run --out json=results.json tests/performance/load-test.js
```

**Expected Throughput:** 1000+ req/s at 200 users

---

## <a id="solutions-architect"></a> 🏛️ Solutions Architect

### Architecture Decision Records (ADRs)

#### ADR 001: Microservices Architecture

**Location:** [`architecture/adr/001-microservices-architecture.md`](architecture/adr/001-microservices-architecture.md)

**115 lines**

**Key Decisions:**
- Adopt microservices over monolith/modular monolith
- Define 7 core services:
  1. User Service (auth, user management)
  2. Product Service (catalog, inventory)
  3. Order Service (order processing)
  4. Payment Service (payment processing)
  5. Notification Service (email, SMS, push)
  6. Search Service (Elasticsearch)
  7. Analytics Service (user behavior)

**Communication Patterns:**
- Synchronous: REST/gRPC for request-response
- Asynchronous: SQS/SNS for events
- Service discovery: AWS Cloud Map / Consul

**Implementation Strategy:**
- Start with 3-4 core services
- API Gateway for unified entry point
- Service mesh (Istio) for observability
- Database per service pattern

---

#### ADR 002: Database Strategy

**Location:** [`architecture/adr/002-database-strategy.md`](architecture/adr/002-database-strategy.md)

**200 lines**

**Key Decisions:**
- Database per service pattern
- Polyglot persistence approach

**Service to Database Mapping:**
- User/Order/Payment → PostgreSQL (ACID requirements)
- Search → Elasticsearch (full-text search)
- Analytics → ClickHouse (time-series aggregations)
- Sessions → Redis (TTL support, fast access)
- Cache → Redis (low latency)

**Consistency Strategy:**
- Strong consistency within service boundaries
- Eventual consistency across services
- Saga pattern for distributed transactions
- Event sourcing for critical workflows

**Code Example Included:**
- Saga pattern implementation with compensating transactions
- Multi-level caching (L1: memory, L2: Redis, L3: database)

**Backup Strategy:**
- Daily automated backups
- Point-in-time recovery (PITR)
- Cross-region replication
- 30-day retention (production)

---

#### ADR 003: API Gateway Pattern

**Location:** [`architecture/adr/003-api-gateway-pattern.md`](architecture/adr/003-api-gateway-pattern.md)

**131 lines**

**Key Decisions:**
- Implement Kong API Gateway
- Centralized authentication and rate limiting

**Features:**
- JWT authentication
- Rate limiting per user/IP (configurable by service)
- Request/response transformation
- Service discovery integration
- Comprehensive logging with Prometheus metrics

**Complete Kong Configuration Included:**
- User Service: 100 req/min rate limit
- Product Service: 1000 req/min rate limit
- Order Service: 50 req/min, 1000 req/hour rate limit
- CORS configuration
- Bot detection
- Request size limiting

**Alternatives Considered:**
- Service-level auth (rejected: duplication)
- AWS API Gateway (rejected: vendor lock-in)
- NGINX+ (rejected: less feature-rich)

---

## <a id="technology-stack"></a> 💻 Technology Stack

### Infrastructure & Cloud
- **IaC:** Terraform 1.0+
- **Cloud Platform:** AWS (VPC, EKS, RDS, CloudWatch, Secrets Manager)
- **Container Orchestration:** Kubernetes 1.28+
- **Container Registry:** GitHub Container Registry (ghcr.io)

### CI/CD & DevOps
- **CI/CD:** GitHub Actions
- **GitOps:** ArgoCD
- **Package Management:** Helm 3.0+
- **Service Mesh:** Istio (referenced)
- **API Gateway:** Kong

### Application & Runtime
- **Runtime:** Node.js 18.x, 20.x
- **Language:** TypeScript
- **Web Framework:** Express.js (implied)
- **Database:** PostgreSQL 15.4
- **Cache:** Redis 7
- **Search:** Elasticsearch

### Testing & Quality
- **Unit Testing:** Jest
- **E2E Testing:** Cypress, Playwright
- **Performance Testing:** K6
- **Security Scanning:** Semgrep, Snyk, Trivy
- **Code Quality:** SonarCloud, ESLint, Prettier
- **Coverage:** Codecov

### Monitoring & Observability
- **Metrics:** Prometheus
- **Dashboards:** Grafana
- **Logging:** CloudWatch, Loki (implied)
- **Tracing:** Distributed tracing (referenced)
- **Alerts:** Alertmanager, PagerDuty

### Security
- **Secrets Management:** AWS Secrets Manager
- **Encryption:** KMS (at rest), TLS (in transit)
- **Authentication:** JWT, OIDC
- **Network Security:** NetworkPolicy, Security Groups
- **Vulnerability Scanning:** Trivy, Snyk

---

## <a id="key-metrics"></a> 📊 Key Metrics

### Code Quality
| Metric | Value | Target |
|--------|-------|--------|
| Total Lines of Code | 2,500+ | - |
| Infrastructure Resources | 50+ AWS resources | - |
| Test Cases | 40+ scenarios | - |
| Code Coverage | >80% | 80% |
| ADRs Documented | 3 major decisions | - |

### Pipeline Performance
| Metric | Value | Target |
|--------|-------|--------|
| Pipeline Stages | 8 stages | - |
| Pipeline Duration | 15-25 min | <30 min |
| Success Rate | - | >95% |
| Deployment Frequency | Multiple/day | Daily+ |

### Application Performance
| Metric | Value | Target |
|--------|-------|--------|
| p95 Response Time | - | <500ms |
| p99 Response Time | - | <1000ms |
| Error Rate | - | <1% |
| Availability SLA | - | 99.9% |
| Concurrent Users | 200 (tested) | - |
| Throughput | 1000+ req/s | - |

### Infrastructure Costs
| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| VPC + NAT Gateways | $45-135 | Per NAT Gateway |
| EKS Cluster | $220-800 | Varies by node count |
| RDS PostgreSQL | $180-450 | Multi-AZ deployment |
| **Total Estimated** | **$445-1,385** | Production setup |

---

## 🎯 Best Practices Demonstrated

### Infrastructure as Code
✅ Modular, reusable Terraform modules
✅ Configuration over hardcoding
✅ DRY (Don't Repeat Yourself) principles
✅ Comprehensive inline documentation
✅ State management with S3 backend + DynamoDB locking

### Security
✅ Defense in depth strategy
✅ Least privilege IAM policies
✅ Encryption at rest (KMS) and in transit (TLS)
✅ Network segmentation with Security Groups
✅ Secrets management (AWS Secrets Manager)
✅ Container security hardening
✅ Vulnerability scanning in CI/CD

### Reliability
✅ Multi-AZ high availability
✅ Auto-scaling (HPA for K8s, ASG for EKS)
✅ Automated backups with 30-day retention
✅ Health probes (liveness, readiness, startup)
✅ Circuit breakers and retry logic
✅ Graceful degradation patterns

### Operations
✅ Comprehensive monitoring (Prometheus metrics)
✅ Centralized logging (CloudWatch)
✅ GitOps deployment model (ArgoCD)
✅ Canary releases with monitoring
✅ Automated rollback capabilities
✅ Infrastructure as Code for reproducibility

### Testing
✅ Test pyramid approach (unit → integration → E2E → performance)
✅ >80% code coverage target
✅ Complete user journey E2E tests
✅ Performance benchmarks with thresholds
✅ API contract testing
✅ Automated test execution in CI/CD

---

## 📚 Additional Resources

### Project Documentation
- [Main Project README](../README.md) - Project overview and objectives
- [Interview Prep Sheet](../INTERVIEW-PREP-SHEET.md) - Talking points for interviews
- [Architecture Diagrams](../ARCHITECTURE-DIAGRAMS.md) - Visual architecture documentation
- [Presentation Deck](../PRESENTATION-DECK.md) - Presentation materials
- [Demo Script](../DEMO-SCRIPT.md) - Live demonstration guide

### Visual Assets
- [Diagrams & Visuals](diagrams/VISUAL-ASSETS-README.md) - Mermaid diagrams and AI prompts

### Code Examples
- [Code Examples README](README.md) - Detailed code walkthrough

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install required tools
terraform >= 1.0
aws-cli >= 2.0
kubectl >= 1.28
helm >= 3.0
node >= 18.x
docker >= 20.x
k6 >= 0.45
```

### Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### Run Tests
```bash
# Unit tests with coverage
npm run test:unit -- --coverage

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# API tests
npx playwright test

# Performance tests
k6 run tests/performance/load-test.js
```

### Deploy with GitOps
```bash
# Apply ArgoCD application
kubectl apply -f cicd/argocd/portfolio-prod.yaml

# Monitor deployment
argocd app get portfolio-production
argocd app sync portfolio-production
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Sam Jackson**
System Development Engineer | DevOps Engineer | QA Engineer

**Connect:**
- [LinkedIn](https://www.linkedin.com/in/sams-jackson)
- [GitHub](https://github.com/samueljackson-collab)

---

**Last Updated:** November 10, 2025
**Version:** 1.0.0
**Status:** ✅ Complete & Production-Ready
