# DevOps Engineer - Data Operations Systems - Lab Tracking Sheet

## Purpose
Track progress through all 12 essential labs covering Kubernetes, Python/Go, CI/CD, cloud platforms, and data operations. Check off each lab and collect portfolio evidence.

---

## 2-Week Lab Schedule Overview

| Week | Focus Area | Labs | Total Hours |
|------|------------|------|-------------|
| Week 1 | DevOps Foundations | Labs 01-05 | 24 hours |
| Week 2 | Advanced & Data Integration | Labs 06-12 | 29 hours |

**Total Lab Time:** 53 hours across 2 weeks (~4 hours/day)

---

## Week 1: DevOps Foundations

### ☐ Lab 01: Local Kubernetes Setup
**Time:** 4 hours | **Priority:** 🔴 CRITICAL | **Difficulty:** Easy-Medium

**Objectives:**
- [ ] Install Docker Desktop or Minikube
- [ ] Deploy nginx pod, expose via Service
- [ ] Test with kubectl port-forward
- [ ] Create ConfigMap and Secret, mount in pod
- [ ] Debug intentional crashing pod

**Prerequisites:**
- Computer with 8GB+ RAM
- Virtualization enabled
- Basic command-line skills

**Setup:**
```bash
# Docker Desktop (Mac/Windows): Enable Kubernetes in settings

# Or Minikube (Linux/Mac/Windows):
brew install minikube
minikube start --cpus 2 --memory 4096

# Verify:
kubectl version
kubectl get nodes
```

**Evidence to Collect:**
- [ ] `kubectl get nodes` output
- [ ] Pod YAML file
- [ ] Service configuration
- [ ] ConfigMap/Secret examples
- [ ] Screenshots of working deployment

**Exercises:**
```bash
# 1. Deploy nginx
kubectl create deployment nginx --image=nginx:latest

# 2. Expose as service
kubectl expose deployment nginx --port=80 --target-port=80

# 3. Port forward to test
kubectl port-forward svc/nginx 8080:80
# Visit http://localhost:8080

# 4. Create ConfigMap
kubectl create configmap my-config --from-literal=key1=value1

# 5. Create Secret
kubectl create secret generic my-secret --from-literal=password=supersecret

# 6. Debug crashing pod (intentional error)
kubectl run broken --image=nginx:broken  # Doesn't exist
kubectl describe pod broken
kubectl logs broken
```

**Validation:**
- [ ] Can create/delete pods, deployments, services
- [ ] Understand difference between Pod, Deployment, Service
- [ ] Can debug CrashLoopBackOff
- [ ] Know how to use ConfigMaps and Secrets

---

### ☐ Lab 02: Python FastAPI Microservice
**Time:** 6 hours | **Priority:** 🔴 CRITICAL | **Difficulty:** Medium

**Objectives:**
- [ ] Build REST API with FastAPI (GET /health, POST /data)
- [ ] Add Pydantic models for request/response validation
- [ ] Implement async endpoint querying database
- [ ] Write pytest tests with 80%+ coverage

**Prerequisites:**
- Python 3.9+ installed
- Basic understanding of REST APIs
- pip or conda

**Setup:**
```bash
pip install fastapi uvicorn pydantic pytest httpx
```

**Evidence to Collect:**
- [ ] FastAPI code with comments
- [ ] Pydantic models
- [ ] Test file with coverage report
- [ ] Postman/curl screenshots

**FastAPI Template:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio

app = FastAPI()

class DataRequest(BaseModel):
    name: str
    value: int

class DataResponse(BaseModel):
    id: int
    name: str
    value: int

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Async endpoint
@app.post("/data", response_model=DataResponse)
async def create_data(data: DataRequest):
    # Simulate async database query
    await asyncio.sleep(0.1)
    return DataResponse(id=1, name=data.name, value=data.value)

# Run with: uvicorn main:app --reload
```

**Tests:**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_data():
    response = client.post("/data", json={"name": "test", "value": 42})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    assert response.json()["value"] == 42

# Run with: pytest --cov=main
```

**Validation:**
- [ ] API runs without errors
- [ ] All tests pass
- [ ] Understands async/await
- [ ] Can explain FastAPI vs Flask

---

### ☐ Lab 03: Dockerize Python App
**Time:** 3 hours | **Priority:** 🔴 CRITICAL | **Difficulty:** Easy-Medium

**Objectives:**
- [ ] Write multi-stage Dockerfile for Python app
- [ ] Build image and run locally
- [ ] Optimize image size (<100MB)
- [ ] Push to Docker Hub or registry

**Prerequisites:**
- Lab 02 completed
- Docker installed
- Docker Hub account (free)

**Evidence to Collect:**
- [ ] Dockerfile with comments
- [ ] Build logs
- [ ] Running container screenshot
- [ ] Image size comparison (before/after optimization)

**Dockerfile Template:**
```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-alpine

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Set path
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Non-root user
RUN adduser -D appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run:**
```bash
# Build
docker build -t myapp:v1.0 .

# Check size
docker images myapp:v1.0

# Run
docker run -d -p 8000:8000 --name myapp myapp:v1.0

# Test
curl http://localhost:8000/health

# Push to registry
docker tag myapp:v1.0 yourusername/myapp:v1.0
docker push yourusername/myapp:v1.0
```

**Validation:**
- [ ] Image builds successfully
- [ ] Container runs without errors
- [ ] Image size optimized (should be <100MB)
- [ ] Understands multi-stage builds

---

### ☐ Lab 04: Deploy to Kubernetes
**Time:** 5 hours | **Priority:** 🔴 CRITICAL | **Difficulty:** Medium-Hard

**Objectives:**
- [ ] Write K8s manifests (Deployment, Service, Ingress)
- [ ] Deploy Dockerized Python app to local K8s
- [ ] Configure liveness/readiness probes
- [ ] Test rolling update (change code, redeploy)

**Prerequisites:**
- Lab 01, 03 completed
- Kubernetes cluster running

**Evidence to Collect:**
- [ ] All YAML manifests
- [ ] kubectl commands used
- [ ] Pod logs showing successful startup
- [ ] Rolling update demonstration

**Kubernetes Manifests:**

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
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
      - name: api
        image: yourusername/myapp:v1.0
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "info"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer  # Or NodePort for local
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Verify
kubectl get deployments
kubectl get pods
kubectl get services

# Test
kubectl port-forward svc/myapp-service 8080:80
curl http://localhost:8080/health

# Rolling update
# Edit deployment.yaml (change image tag to v1.1)
kubectl apply -f deployment.yaml
kubectl rollout status deployment/myapp

# Rollback if needed
kubectl rollout undo deployment/myapp
```

**Validation:**
- [ ] All pods running
- [ ] Service accessible
- [ ] Probes working (check events)
- [ ] Can perform rolling updates

---

### ☐ Lab 05: GitLab CI/CD Pipeline
**Time:** 6 hours | **Priority:** 🔴 CRITICAL | **Difficulty:** Medium-Hard

**Objectives:**
- [ ] Create .gitlab-ci.yml with stages: test, build, deploy
- [ ] Run pytest in CI
- [ ] Build Docker image and push to registry
- [ ] Deploy to K8s using kubectl in CI job

**Prerequisites:**
- Lab 02-04 completed
- GitLab account (free)
- GitLab Runner configured (or use shared runners)

**Evidence to Collect:**
- [ ] .gitlab-ci.yml file
- [ ] Successful pipeline screenshots
- [ ] Failed pipeline (intentional) and how you fixed it

**.gitlab-ci.yml Template:**
```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  DOCKER_LATEST: $CI_REGISTRY_IMAGE:latest

# Test stage
test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest --cov=main --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'

# Build stage
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE -t $DOCKER_LATEST .
    - docker push $DOCKER_IMAGE
    - docker push $DOCKER_LATEST
  only:
    - main

# Deploy stage
deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config set-cluster k8s --server="$KUBE_SERVER" --insecure-skip-tls-verify=true
    - kubectl config set-credentials admin --token="$KUBE_TOKEN"
    - kubectl config set-context default --cluster=k8s --user=admin
    - kubectl config use-context default
    - kubectl set image deployment/myapp api=$DOCKER_IMAGE
    - kubectl rollout status deployment/myapp
  only:
    - main
  when: manual  # Require manual approval for deploy
```

**Setup GitLab CI Variables:**
- `CI_REGISTRY` = registry.gitlab.com
- `CI_REGISTRY_USER` = gitlab username
- `CI_REGISTRY_PASSWORD` = GitLab token
- `KUBE_SERVER` = Kubernetes API server URL
- `KUBE_TOKEN` = Kubernetes service account token

**Validation:**
- [ ] All pipeline stages pass
- [ ] Can trigger manual deployment
- [ ] Understands GitLab CI stages and jobs
- [ ] Can troubleshoot failed pipelines

---

## Week 2: Advanced & Data Integration

### ☐ Lab 06: Go Microservice Basics
**Time:** 5 hours | **Priority:** 🟡 HIGH | **Difficulty:** Medium

**Objectives:**
- [ ] Build simple Go HTTP server with /health endpoint
- [ ] Add middleware for logging and auth
- [ ] Connect to Postgres, implement CRUD
- [ ] Write Go tests

**Prerequisites:**
- Go 1.21+ installed
- Basic programming knowledge

**Setup:**
```bash
# Install Go: https://go.dev/dl/
go version

# Create project
mkdir mygoapp && cd mygoapp
go mod init mygoapp
```

**Evidence to Collect:**
- [ ] Go code with comments
- [ ] Test file
- [ ] Running server screenshot
- [ ] Database queries working

**Go HTTP Server Template:**
```go
package main

import (
    "database/sql"
    "encoding/json"
    "log"
    "net/http"
    "time"

    _ "github.com/lib/pq"
)

type HealthResponse struct {
    Status string `json:"status"`
    Time   string `json:"time"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    response := HealthResponse{
        Status: "healthy",
        Time:   time.Now().Format(time.RFC3339),
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("%s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/health", healthHandler)

    handler := loggingMiddleware(mux)

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", handler))
}
```

**Run:**
```bash
go run main.go
# Test: curl http://localhost:8080/health
```

**Validation:**
- [ ] Server runs without errors
- [ ] Middleware working
- [ ] Tests pass
- [ ] Understands goroutines and channels

---

### ☐ Lab 07: Snowflake Integration
**Time:** 5 hours | **Priority:** 🟡 HIGH | **Difficulty:** Medium

**Objectives:**
- [ ] Sign up for Snowflake trial
- [ ] Create database, schema, table
- [ ] Python script to load data to Snowflake
- [ ] Query data and return results via API endpoint

**Prerequisites:**
- Lab 02 completed (FastAPI)
- Snowflake account (free trial)

**Evidence to Collect:**
- [ ] Snowflake queries (DDL, DML)
- [ ] Python code connecting to Snowflake
- [ ] API endpoint returning Snowflake data

**Setup:**
```bash
pip install snowflake-connector-python
```

**Python + Snowflake:**
```python
import snowflake.connector
from fastapi import FastAPI

app = FastAPI()

# Snowflake connection
def get_snowflake_conn():
    return snowflake.connector.connect(
        user='YOUR_USER',
        password='YOUR_PASSWORD',
        account='YOUR_ACCOUNT',
        warehouse='COMPUTE_WH',
        database='MY_DB',
        schema='PUBLIC'
    )

@app.get("/data")
async def get_data():
    conn = get_snowflake_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM my_table LIMIT 10")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"data": results}
```

**Validation:**
- [ ] Can connect to Snowflake from Python
- [ ] Can query and insert data
- [ ] API serves Snowflake data
- [ ] Understands Snowflake virtual warehouses

---

### ☐ Lab 08: Azure EntraID Authentication
**Time:** 6 hours | **Priority:** 🟡 HIGH | **Difficulty:** Hard

**Objectives:**
- [ ] Create Azure free account
- [ ] Register application in EntraID
- [ ] Secure Python API with EntraID OAuth2
- [ ] Test with Postman (acquire token, call API)

**Prerequisites:**
- Lab 02 completed
- Azure account

**Evidence to Collect:**
- [ ] EntraID app registration screenshots
- [ ] Python auth code
- [ ] Successful authentication flow (Postman)

**Setup:**
1. Azure Portal → EntraID → App Registrations → New
2. Configure redirect URI, API permissions
3. Create client secret

**Python + EntraID:**
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

AZURE_AD_TENANT_ID = "YOUR_TENANT_ID"
AZURE_AD_CLIENT_ID = "YOUR_CLIENT_ID"

def verify_token(token: str):
    # Verify JWT token with Azure AD
    jwks_uri = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
    # Token verification logic here
    return True  # Simplified for example

@app.get("/secure-data")
async def secure_data(token: str = Depends(oauth2_scheme)):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Secure data"}
```

**Validation:**
- [ ] Can register app in EntraID
- [ ] Can acquire OAuth2 token
- [ ] API validates tokens correctly
- [ ] Understands OAuth2 flows

---

### ☐ Lab 09: Helm Chart Creation
**Time:** 4 hours | **Priority:** 🟡 MEDIUM | **Difficulty:** Medium

**Objectives:**
- [ ] Create Helm chart for Python microservice
- [ ] Parameterize values (replicas, image tag, env vars)
- [ ] Install chart with different values for dev/prod
- [ ] Upgrade and rollback releases

**Prerequisites:**
- Lab 04 completed
- Helm installed

**Setup:**
```bash
brew install helm  # Or: choco install kubernetes-helm
helm version
```

**Evidence to Collect:**
- [ ] Helm chart files
- [ ] helm install output
- [ ] Different values.yaml for dev/prod

**Create Chart:**
```bash
helm create myapp-chart
cd myapp-chart

# Edit values.yaml, templates/deployment.yaml, etc.
```

**Install:**
```bash
# Dev environment
helm install myapp-dev ./myapp-chart -f values-dev.yaml

# Prod environment
helm install myapp-prod ./myapp-chart -f values-prod.yaml

# Upgrade
helm upgrade myapp-dev ./myapp-chart

# Rollback
helm rollback myapp-dev 1
```

**Validation:**
- [ ] Chart installs successfully
- [ ] Can customize via values.yaml
- [ ] Can upgrade/rollback
- [ ] Understands Helm templates

---

### ☐ Lab 10: AWS S3 + Lambda Integration
**Time:** 4 hours | **Priority:** 🟡 MEDIUM | **Difficulty:** Medium

**Objectives:**
- [ ] Create S3 bucket and Lambda function
- [ ] Configure S3 event trigger (on file upload)
- [ ] Lambda processes file, writes to SQS or DynamoDB
- [ ] Test end-to-end flow

**Prerequisites:**
- AWS account (free tier)
- Basic Python knowledge

**Evidence to Collect:**
- [ ] Lambda code
- [ ] S3 event configuration
- [ ] Test execution logs

**Lambda Function (Python):**
```python
import json
import boto3

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    # Get S3 bucket and key from event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    print(f"Processing file: s3://{bucket}/{key}")

    # Read file from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')

    # Process data (example: count lines)
    line_count = len(data.split('\n'))

    # Send to SQS
    sqs.send_message(
        QueueUrl='YOUR_QUEUE_URL',
        MessageBody=json.dumps({
            'file': key,
            'lines': line_count
        })
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {line_count} lines')
    }
```

**Validation:**
- [ ] Lambda triggered on S3 upload
- [ ] File processed successfully
- [ ] SQS message sent
- [ ] Understands event-driven architecture

---

### ☐ Lab 11: Prometheus Metrics
**Time:** 4 hours | **Priority:** 🟡 MEDIUM | **Difficulty:** Medium

**Objectives:**
- [ ] Add Prometheus client library to Python API
- [ ] Expose /metrics endpoint
- [ ] Add custom metrics (request count, latency, errors)
- [ ] Run Prometheus locally, scrape API
- [ ] Create simple Grafana dashboard

**Prerequisites:**
- Lab 02 completed
- Docker installed

**Setup:**
```bash
pip install prometheus-client
```

**Python + Prometheus:**
```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI, Response

app = FastAPI()

# Define metrics
request_count = Counter(
    'api_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    with request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).time():
        response = await call_next(request)

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    return response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

**Run Prometheus:**
```bash
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['host.docker.internal:8000']

# Run Prometheus
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

**Validation:**
- [ ] /metrics endpoint works
- [ ] Prometheus scraping API
- [ ] Can query metrics in Prometheus UI
- [ ] Grafana dashboard created

---

### ☐ Lab 12: Complete GitOps Deployment (Capstone)
**Time:** 6 hours | **Priority:** 🔴 CRITICAL | **Difficulty:** Hard

**Objectives:**
- [ ] Combine Labs 1-11 into full stack
- [ ] GitLab CI/CD builds Docker image
- [ ] Updates Helm chart values
- [ ] Deploys to K8s automatically on git push
- [ ] Metrics visible in Grafana

**Prerequisites:**
- All previous labs completed

**Evidence to Collect:**
- [ ] End-to-end flow documentation
- [ ] Architecture diagram
- [ ] All code and configs
- [ ] Demo video/screenshots

**Architecture:**
```
[Git Push] → [GitLab CI/CD] → [Build Docker] → [Push to Registry]
                ↓
         [Update Helm Values] → [Deploy to Kubernetes]
                ↓
         [Prometheus Scrapes Metrics] → [Grafana Dashboard]
```

**Validation:**
- [ ] Full pipeline works end-to-end
- [ ] Can explain every component
- [ ] Ready to present in interview
- [ ] Code is production-ready

---

## Progress Tracking

**Week 1:** ☐☐☐☐☐ (0/5)
**Week 2:** ☐☐☐☐☐☐☐ (0/7)
**Overall:** 0/12 (0%)

---

**Last Updated:** 2025-11-11
**For Role:** DevOps Engineer - Data Operations Systems (T-Mobile)
**Compensation:** $48-56/hr (~$100-117K/year)
