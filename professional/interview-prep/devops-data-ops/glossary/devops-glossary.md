# DevOps Engineer - Data Operations Systems - Comprehensive Glossary

## Purpose
This glossary covers DevOps, Kubernetes, CI/CD, cloud (Azure/AWS), Python/Go, and data operations terminology for the T-Mobile DevOps Engineer role. Use as quick reference for study and interviews.

---

## A

**ACR (Azure Container Registry)**
- Azure's private Docker container registry
- Stores and manages container images
- Integrates with AKS for automated deployments
- Similar to: Docker Hub, ECR (AWS), GCR (Google)

**AKS (Azure Kubernetes Service)**
- Managed Kubernetes service on Azure
- Azure handles control plane (master nodes)
- You manage: Worker nodes, applications
- Features: Auto-scaling, monitoring, Azure AD integration

**ALB (Application Load Balancer - AWS)**
- Layer 7 (application) load balancer
- Routes traffic based on: URL path, hostname, headers
- Integrates with: ECS, EKS, EC2
- Example: `/api/*` → API service, `/web/*` → Web service

**API (Application Programming Interface)**
- Interface for software components to communicate
- REST API: HTTP-based, stateless
- GraphQL: Query language for APIs
- gRPC: High-performance RPC framework

**ARM (Azure Resource Manager)**
- Azure's deployment and management service
- Infrastructure as Code: ARM templates (JSON)
- Alternative: Terraform, Bicep

**async/await (Python)**
- Syntax for asynchronous programming
- async def: Defines coroutine (async function)
- await: Pauses execution until awaited operation completes
- Benefits: Non-blocking I/O, high concurrency

---

## B

**Base Image (Docker)**
- Starting point for Docker image
- Specified with FROM in Dockerfile
- Examples: `FROM python:3.11-slim`, `FROM golang:1.21-alpine`
- Smaller base = faster builds, smaller images

**Blob Storage (Azure)**
- Azure's object storage service (like AWS S3)
- Types: Block blobs (files), Page blobs (VMs), Append blobs (logs)
- Use cases: Backups, data lakes, static websites
- Access: REST API, SDKs, Azure CLI

**boto3 (Python)**
- AWS SDK for Python
- Interact with: S3, Lambda, SQS, DynamoDB, etc.
- Example: `s3 = boto3.client('s3'); s3.upload_file('file.txt', 'bucket', 'key')`

---

## C

**CAPEX (Capital Expenditure)**
- Upfront spending on physical infrastructure
- Example: Buying servers, data center costs
- Cloud shifts to OPEX (operational expense - pay-as-you-go)

**CI/CD (Continuous Integration / Continuous Deployment)**
- CI: Automatically build and test code on every commit
- CD: Automatically deploy tested code to production
- Benefits: Faster releases, fewer bugs, automated testing
- Tools: GitLab CI/CD, Jenkins, GitHub Actions, Azure DevOps

**Circuit Breaker**
- Design pattern preventing cascading failures
- If service fails repeatedly, stop calling it (give it time to recover)
- States: Closed (normal), Open (failing, stop calls), Half-Open (testing recovery)
- Python library: `circuitbreaker`

**CLI (Command Line Interface)**
- Text-based interface for tools/services
- kubectl: Kubernetes CLI
- az: Azure CLI
- aws: AWS CLI
- docker: Docker CLI

**ConfigMap (Kubernetes)**
- Kubernetes object storing configuration as key-value pairs
- Non-sensitive data (for secrets, use Secret object)
- Mounted as: Environment variables or files
- Example: Database connection string, feature flags

**Container**
- Lightweight, portable package containing app + dependencies
- Isolated from host OS (uses Linux namespaces, cgroups)
- Built from: Docker image
- Run with: Docker, containerd, Kubernetes

**Context (Go)**
- Carries deadlines, cancellation signals, request-scoped values
- Use: Timeouts, cancellation, passing request metadata
- Example: `ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)`

**Coroutine (Python)**
- Function defined with `async def`
- Can be paused and resumed (non-blocking)
- Must be awaited or scheduled in event loop
- Example: `async def fetch_data(): ...`

**CrashLoopBackOff (Kubernetes)**
- Pod status indicating container repeatedly crashing
- Kubernetes tries to restart with exponential backoff (10s, 20s, 40s, ...)
- Common causes: Application error, missing config, OOMKilled

---

## D

**DaemonSet (Kubernetes)**
- Ensures pod runs on all (or selected) nodes
- Use cases: Logging agents, monitoring agents, storage daemons
- Example: Fluentd on every node collecting logs

**Deployment (Kubernetes)**
- Manages stateless application replicas
- Features: Rolling updates, rollbacks, scaling
- Example: Web application with 3 replicas

**Docker**
- Platform for developing, shipping, running containers
- Components: Docker Engine, Docker CLI, Docker Hub (registry)
- Dockerfile: Text file defining image build steps
- Example: `docker build -t myapp:v1 .`

**Dockerfile**
- Script defining how to build Docker image
- Instructions: FROM (base), COPY (files), RUN (commands), CMD (startup)
- Best practice: Multi-stage builds (smaller final image)

---

## E

**ECR (Elastic Container Registry - AWS)**
- AWS's private Docker container registry
- Integrates with ECS, EKS
- Features: Image scanning, lifecycle policies

**EKS (Elastic Kubernetes Service - AWS)**
- AWS's managed Kubernetes service
- Similar to: AKS (Azure), GKE (Google)

**EntraID (Microsoft Entra ID)**
- Formerly Azure Active Directory (Azure AD)
- Cloud-based identity and access management
- Features: Authentication, authorization, SSO, MFA
- OAuth2/OIDC flows for API authentication

**ENV (Environment Variable)**
- Configuration value passed to application at runtime
- Example: `DATABASE_URL=postgres://user:pass@host:5432/db`
- Kubernetes: Set in ConfigMap, Secret, or pod spec directly

**Event-Driven Architecture**
- System where services react to events
- Example: S3 file uploaded → Lambda triggered → Process file → Write to SQS
- Benefits: Loose coupling, scalability, asynchronous

---

## F

**FastAPI (Python)**
- Modern web framework for building APIs
- Features: Async support, automatic OpenAPI docs, type validation (Pydantic)
- Performance: Comparable to Node.js, Go (due to async)
- Example: `@app.get("/users/{user_id}") async def get_user(user_id: int): ...`

**Flask (Python)**
- Lightweight web framework
- Synchronous by default (can use async with Flask 2.0+)
- Use FastAPI for: High-performance async APIs
- Use Flask for: Simple synchronous apps, legacy systems

---

## G

**GitLab CI/CD**
- CI/CD platform built into GitLab
- Configuration: .gitlab-ci.yml file
- Concepts: Pipelines, stages, jobs, runners
- Example stages: test → build → deploy

**GitOps**
- Using Git as single source of truth for infrastructure/apps
- Changes: Pull requests update Git repo → Automated deployment
- Tools: ArgoCD, Flux
- Benefits: Auditable, reproducible, easy rollbacks

**Go (Golang)**
- Statically typed, compiled programming language (Google)
- Features: Fast compilation, concurrency (goroutines), small binaries
- Use cases: Microservices, CLI tools, cloud infrastructure
- Example: Docker, Kubernetes written in Go

**Goroutine (Go)**
- Lightweight thread managed by Go runtime
- Start with: `go funcName()`
- Thousands of goroutines can run simultaneously
- Communication: Channels

**Grafana**
- Visualization and dashboarding platform
- Data sources: Prometheus, InfluxDB, CloudWatch, many more
- Use: Monitor metrics, create alerts, build dashboards

---

## H

**HCL (HashiCorp Configuration Language)**
- Configuration language for Terraform
- Human-readable, declarative
- Example: `resource "aws_instance" "web" { ami = "ami-123456" }`

**Health Check**
- Endpoint indicating service health
- Kubernetes: Liveness and readiness probes
- Example: `GET /health` returns 200 if healthy, 503 if unhealthy

**Helm**
- Package manager for Kubernetes
- Charts: Bundled Kubernetes manifests with templating
- Commands: `helm install`, `helm upgrade`, `helm rollback`
- Values: Parameterize manifests (dev vs. prod configs)

**HorizontalPodAutoscaler (Kubernetes)**
- Automatically scales pod replicas based on metrics
- Metrics: CPU, memory, custom (e.g., request rate)
- Example: Scale from 2-10 pods based on 70% CPU threshold

---

## I

**IAM (Identity and Access Management)**
- AWS: Control access to AWS resources
- Azure: Azure AD/EntraID
- Concepts: Users, roles, policies, permissions

**IaC (Infrastructure as Code)**
- Managing infrastructure via code (not manual)
- Tools: Terraform, CloudFormation, ARM templates, Pulumi
- Benefits: Version control, reproducibility, automation

**Image (Docker)**
- Read-only template for creating containers
- Layers: Each Dockerfile instruction = layer
- Registry: Docker Hub, ACR, ECR, GCR
- Tags: Version identifier (e.g., `myapp:v1.2.3`)

**Ingress (Kubernetes)**
- Kubernetes object managing external HTTP/HTTPS access to services
- Features: Load balancing, SSL termination, name-based virtual hosting
- Controllers: NGINX, Traefik, HAProxy, cloud-specific (ALB, GCE)

**Init Container (Kubernetes)**
- Container running before app container starts
- Use cases: Wait for dependencies, setup tasks, file downloads
- Example: Wait for database to be ready before starting app

---

## J

**Jinja (Jinja2)**
- Templating engine for Python
- Used in: Helm charts (YAML templating), Ansible, Flask
- Syntax: `{{ variable }}`, `{% for item in list %}`, `{% if condition %}`

**JSON (JavaScript Object Notation)**
- Lightweight text-based data format
- Key-value pairs: `{"name": "Alice", "age": 30}`
- Used in: APIs, configuration files, data exchange

---

## K

**kubectl**
- Command-line tool for Kubernetes
- Common commands:
  - `kubectl get pods` - List pods
  - `kubectl describe pod <name>` - Detailed pod info
  - `kubectl logs <pod>` - View logs
  - `kubectl exec -it <pod> -- /bin/sh` - Shell into container
  - `kubectl apply -f manifest.yaml` - Create/update resources

**Kubernetes (K8s)**
- Open-source container orchestration platform
- Features: Auto-scaling, self-healing, load balancing, rolling updates
- Components: Control plane (API server, scheduler, controller manager), Worker nodes (kubelet, kube-proxy, container runtime)

---

## L

**Lambda (AWS)**
- Serverless compute service
- Run code without managing servers
- Triggered by: Events (S3 upload, API Gateway, SQS message)
- Pricing: Pay per invocation and compute time

**Liveness Probe (Kubernetes)**
- Check if container is alive
- If fails: Kubernetes restarts container
- Example: `GET /health` every 10 seconds

**Load Balancer**
- Distributes traffic across multiple servers
- Types: Layer 4 (TCP/UDP), Layer 7 (HTTP/HTTPS)
- Kubernetes: Service type=LoadBalancer

**Logging**
- Recording application events for debugging/monitoring
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structured logging: JSON format (easier to parse)
- Tools: ELK stack, Splunk, CloudWatch, Azure Monitor

---

## M

**Managed Identity (Azure)**
- Identity for Azure resources (no need to store credentials)
- Types: System-assigned (tied to resource), User-assigned (shared)
- Use: App Service accesses Key Vault without password

**Manifest (Kubernetes)**
- YAML/JSON file defining Kubernetes resource
- Example: Deployment, Service, ConfigMap manifests
- Apply with: `kubectl apply -f deployment.yaml`

**Microservices**
- Architectural pattern: Application as collection of small, independent services
- Benefits: Scalability, independent deployment, technology diversity
- Challenges: Complexity, distributed debugging, network overhead

**Multi-Stage Build (Docker)**
- Dockerfile with multiple FROM statements
- Use: Build in one stage, copy artifacts to smaller final image
- Benefits: Smaller images, faster pulls, reduced attack surface

---

## N

**Namespace (Kubernetes)**
- Virtual cluster within physical cluster
- Isolate resources: dev, staging, prod
- Default namespaces: default, kube-system, kube-public

**NGINX**
- Web server and reverse proxy
- Use cases: Load balancing, SSL termination, ingress controller
- Kubernetes: NGINX Ingress Controller

**Node (Kubernetes)**
- Worker machine (VM or physical)
- Runs: kubelet (agent), kube-proxy (networking), container runtime
- Can run multiple pods

---

## O

**OAuth2**
- Authorization framework for delegated access
- Flows: Authorization Code, Client Credentials, Implicit, ROPC
- Example: "Allow App X to access your Google Drive"

**OIDC (OpenID Connect)**
- Identity layer on top of OAuth2
- Provides: Authentication, user info
- Used by: EntraID, Google Sign-In, Okta

**OOMKilled (Out Of Memory Killed)**
- Container terminated because it exceeded memory limit
- Exit code: 137
- Fix: Increase memory limit or optimize app

**OPEX (Operational Expenditure)**
- Ongoing costs for running business
- Cloud: Pay-as-you-go (contrasts with CAPEX)

---

## P

**Pandas (Python)**
- Data manipulation library
- Core: DataFrame (tabular data)
- Operations: Read CSV/SQL, filter, group, merge
- Use: ETL, data analysis, data cleaning

**PersistentVolume (Kubernetes)**
- Cluster-level storage resource
- Lifecycle independent of pods
- Types: EBS (AWS), Azure Disk, NFS, Ceph

**PersistentVolumeClaim (Kubernetes)**
- Request for storage by pod
- Binds to PersistentVolume
- Example: Database pod needs persistent disk

**Pod (Kubernetes)**
- Smallest deployable unit (one or more containers)
- Shares: Network namespace (IP), storage volumes
- Ephemeral: Recreated on failures

**Prometheus**
- Open-source monitoring and alerting system
- Data model: Time-series (metric name + labels)
- Metrics types: Counter, Gauge, Histogram, Summary
- Querying: PromQL (Prometheus Query Language)
- Scraping: Pulls metrics from /metrics endpoints

**Pydantic (Python)**
- Data validation library using Python type hints
- Used by: FastAPI (request/response validation)
- Example: `class User(BaseModel): name: str; age: int`

**pytest (Python)**
- Testing framework
- Features: Fixtures, parametrized tests, plugins
- Example: `def test_addition(): assert 1 + 1 == 2`

---

## R

**RBAC (Role-Based Access Control)**
- Authorization model based on roles
- Kubernetes: Roles, ClusterRoles, RoleBindings
- Azure: Azure RBAC (Reader, Contributor, Owner roles)

**Readiness Probe (Kubernetes)**
- Check if container ready to serve traffic
- If fails: Pod removed from service endpoints (but not restarted)
- Example: Database connection established

**Redis**
- In-memory data store (key-value)
- Use cases: Caching, session storage, message broker
- Data structures: Strings, lists, sets, sorted sets, hashes

**Registry (Container)**
- Storage for Docker images
- Public: Docker Hub
- Private: ACR, ECR, GCR, self-hosted

**ReplicaSet (Kubernetes)**
- Ensures specified number of pod replicas running
- Typically managed by Deployment (don't create directly)

**REST (Representational State Transfer)**
- Architectural style for APIs
- HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete)
- Stateless, resource-based URLs

**Rollback (Deployment)**
- Reverting to previous version
- Kubernetes: `kubectl rollout undo deployment/myapp`
- GitLab CI/CD: Redeploy previous pipeline

**Rolling Update (Kubernetes)**
- Gradual replacement of old pods with new ones
- Zero downtime deployments
- Configurable: maxSurge, maxUnavailable

---

## S

**S3 (Simple Storage Service - AWS)**
- Object storage service
- Buckets: Container for objects
- Use cases: Data lakes, backups, static websites
- Access: REST API, SDKs, CLI

**Secret (Kubernetes)**
- Kubernetes object storing sensitive data (base64 encoded)
- Types: Opaque (generic), TLS, docker-registry
- Mounted as: Environment variables or files
- Example: Database password, API keys

**Service (Kubernetes)**
- Stable network endpoint for pods
- Types:
  - ClusterIP: Internal only (default)
  - NodePort: External access via node IP + port
  - LoadBalancer: External load balancer (cloud provider)
  - ExternalName: DNS CNAME alias

**Service Principal (Azure)**
- Identity for applications accessing Azure resources
- Like IAM role in AWS
- Has: Client ID, client secret, tenant ID

**Sidecar (Kubernetes)**
- Additional container in same pod as main container
- Use cases: Logging, monitoring, proxying
- Example: Envoy proxy alongside app container

**SNS (Simple Notification Service - AWS)**
- Pub/sub messaging service
- Publishers send to topics, subscribers receive
- Protocols: HTTP, email, SMS, SQS, Lambda

**SQS (Simple Queue Service - AWS)**
- Message queue service
- Types: Standard (at-least-once, best-effort ordering), FIFO (exactly-once, strict ordering)
- Use: Decouple services, asynchronous processing

**StatefulSet (Kubernetes)**
- Manages stateful applications
- Features: Stable network IDs, ordered deployment, persistent storage
- Use: Databases, Kafka, Zookeeper

---

## T

**Terraform**
- Infrastructure as Code tool (HashiCorp)
- Multi-cloud: AWS, Azure, GCP, Kubernetes
- HCL syntax: `resource`, `module`, `variable`
- State management: Tracks actual infrastructure

**TLS (Transport Layer Security)**
- Cryptographic protocol for secure communication
- Formerly SSL (Secure Sockets Layer)
- HTTPS = HTTP over TLS
- Kubernetes: Ingress with TLS termination

---

## U

**Unit Test**
- Test for individual function/method
- Isolated: No external dependencies (use mocks)
- Fast: Hundreds of tests run in seconds
- Tools: pytest (Python), testing (Go)

---

## V

**Virtual Warehouse (Snowflake)**
- See Backend Snowflake glossary

**Volume (Kubernetes)**
- Directory accessible to containers in pod
- Types: emptyDir (temporary), hostPath (node filesystem), PersistentVolume (persistent)

---

## W

**Webhook**
- HTTP callback triggered by event
- Example: GitHub webhook triggers GitLab pipeline on push
- GitLab uses: For CI/CD triggers

---

## Y

**YAML (YAML Ain't Markup Language)**
- Human-readable data serialization format
- Used in: Kubernetes manifests, Helm charts, CI/CD configs
- Syntax: Key-value pairs, indentation-based hierarchy
- Example:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: myapp
  ```

---

## Quick Reference: Kubernetes Resource Types

| Resource | Purpose | Example Use |
|----------|---------|-------------|
| Pod | Smallest unit (container(s)) | Single instance of app |
| Deployment | Manages stateless app replicas | Web application |
| StatefulSet | Manages stateful app replicas | Database cluster |
| DaemonSet | Pod on every node | Logging agent |
| Service | Stable network endpoint | Load balance across pods |
| Ingress | HTTP/HTTPS routing | External access with SSL |
| ConfigMap | Configuration data | App settings |
| Secret | Sensitive data | Passwords, API keys |
| PersistentVolume | Storage | Database storage |
| Namespace | Virtual cluster | dev, staging, prod isolation |

---

## Quick Reference: kubectl Commands

| Command | Purpose |
|---------|---------|
| `kubectl get pods` | List pods |
| `kubectl describe pod <name>` | Detailed pod info |
| `kubectl logs <pod>` | View logs |
| `kubectl logs <pod> --previous` | Logs from crashed container |
| `kubectl exec -it <pod> -- /bin/sh` | Shell into container |
| `kubectl apply -f <file>` | Create/update resources |
| `kubectl delete pod <name>` | Delete pod |
| `kubectl get events` | Cluster events |
| `kubectl port-forward <pod> 8080:80` | Forward local port to pod |
| `kubectl scale deployment <name> --replicas=5` | Scale deployment |
| `kubectl rollout status deployment/<name>` | Deployment status |
| `kubectl rollout undo deployment/<name>` | Rollback deployment |

---

## Quick Reference: Docker Commands

| Command | Purpose |
|---------|---------|
| `docker build -t myapp:v1 .` | Build image |
| `docker run -p 8080:80 myapp:v1` | Run container |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker logs <container>` | View logs |
| `docker exec -it <container> /bin/sh` | Shell into container |
| `docker stop <container>` | Stop container |
| `docker rm <container>` | Remove container |
| `docker images` | List images |
| `docker rmi <image>` | Remove image |
| `docker push myapp:v1` | Push to registry |
| `docker pull myapp:v1` | Pull from registry |

---

## Quick Reference: HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service down/overloaded |

---

## Quick Reference: Prometheus Metric Types

| Type | Purpose | Example | When to Use |
|------|---------|---------|-------------|
| Counter | Cumulative value (only increases) | `api_requests_total` | Count events (requests, errors) |
| Gauge | Value that can go up or down | `memory_usage_bytes` | Current state (memory, queue size) |
| Histogram | Distribution of values | `request_duration_seconds` | Latency, size distributions |
| Summary | Similar to histogram, calculated client-side | `request_duration_seconds` | Latency percentiles |

---

**Last Updated:** 2025-11-11
**For Role:** DevOps Engineer - Data Operations Systems (T-Mobile)
**Compensation:** $48-56/hr (~$100-117K/year)

**Usage Tips:**
- Use Ctrl+F to quickly find terms
- Cross-reference with expanded cheat sheets for deeper explanations
- Practice kubectl commands hands-on (essential for role)
- Review Kubernetes resource types (most interview questions focus here)
- Understand async Python and goroutines (core to performance)
- Memorize HTTP status codes (API development essential)
