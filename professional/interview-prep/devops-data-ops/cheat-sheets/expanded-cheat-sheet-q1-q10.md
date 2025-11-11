# DevOps Engineer - Data Operations Systems - Expanded Cheat Sheet (Q1-Q10)

## Question 1: Kubernetes Pod Troubleshooting

**Question:** How would you debug a CrashLoopBackOff pod? Walk me through your systematic approach.

**Feynman Explanation:**
CrashLoopBackOff is like a car that keeps stalling every time you start it. The engine turns on, runs for a few seconds, then dies. Kubernetes keeps trying to restart it (that's the "loop"), but the wait time gets longer each time (that's the "backoff"). To fix it, you need to find out WHY it's crashing: Bad fuel? (wrong config) Missing parts? (missing dependencies) Wrong key? (authentication failure). You check the logs (like a black box recorder) to see what happened right before the crash.

**Technical Answer:**

**CrashLoopBackOff Explained:**
- Pod starts successfully
- Container runs for short time, then exits with error
- Kubernetes automatically restarts it
- Container crashes again
- Kubernetes waits longer before next restart (exponential backoff: 10s, 20s, 40s, 80s, up to 5 min)
- Status shows: `CrashLoopBackOff`

**Systematic Troubleshooting Process:**

**Step 1: Check Pod Status**
```bash
kubectl get pods
# Output:
# NAME                    READY   STATUS             RESTARTS   AGE
# myapp-7d8f9c-k2p4x      0/1     CrashLoopBackOff   5          10m

# Get detailed status
kubectl describe pod myapp-7d8f9c-k2p4x
```

**Key things to look for in `describe`:**

```yaml
# Look at Events section (bottom):
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  5m                 default-scheduler  Successfully assigned default/myapp-7d8f9c-k2p4x to node1
  Normal   Pulling    5m                 kubelet            Pulling image "myapp:v1.0"
  Normal   Pulled     5m                 kubelet            Successfully pulled image
  Warning  BackOff    2m (x5 over 4m)    kubelet            Back-off restarting failed container

# Look at Last State:
Last State:     Terminated
  Reason:       Error
  Exit Code:    1  <-- Non-zero exit = crash
  Started:      Mon, 11 Nov 2024 10:00:00 -0700
  Finished:     Mon, 11 Nov 2024 10:00:05 -0700
```

**Step 2: Check Container Logs**
```bash
# Current logs (if container is running)
kubectl logs myapp-7d8f9c-k2p4x

# Previous logs (from crashed container)
kubectl logs myapp-7d8f9c-k2p4x --previous

# Follow logs in real-time
kubectl logs myapp-7d8f9c-k2p4x -f

# If pod has multiple containers
kubectl logs myapp-7d8f9c-k2p4x -c <container-name>
```

**Common Log Errors:**

**A. Application Error**
```
Error: Cannot find module '/app/server.js'
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:636:15)
```
→ **Fix:** Wrong working directory or missing file in Docker image

**B. Port Already in Use**
```
Error: listen EADDRINUSE: address already in use :::8080
```
→ **Fix:** Another process using port or hostPort conflict

**C. Environment Variable Missing**
```
Error: DATABASE_URL environment variable not set
```
→ **Fix:** Add env var to pod spec

**D. Connection Refused**
```
Error: connect ECONNREFUSED 10.96.0.1:5432
    at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:16)
```
→ **Fix:** Database service not ready or wrong service name

**Step 3: Check ConfigMaps and Secrets**
```bash
# Check if ConfigMap/Secret exists
kubectl get configmaps
kubectl get secrets

# Describe to see keys (values are hidden for secrets)
kubectl describe configmap myapp-config
kubectl describe secret myapp-secret

# If ConfigMap missing or wrong, app will fail
```

**Step 4: Check Liveness/Readiness Probes**
```bash
kubectl describe pod myapp-7d8f9c-k2p4x | grep -A 10 "Liveness\|Readiness"
```

**Problem:** Probe fails, Kubernetes kills pod
```yaml
Liveness:       http-get http://:8080/health delay=10s timeout=1s period=10s
# If /health endpoint doesn't respond in 1s, probe fails
# After 3 failures, container is killed (CrashLoopBackOff)
```

**Fix:**
- Increase probe timeout
- Increase initialDelaySeconds (app needs more time to start)
- Fix /health endpoint to respond correctly

**Step 5: Check Resource Limits**
```bash
kubectl describe pod myapp-7d8f9c-k2p4x | grep -A 5 "Limits\|Requests"
```

**Problem:** Out of Memory (OOMKilled)
```yaml
Last State:     Terminated
  Reason:       OOMKilled  <-- Container used more memory than limit
  Exit Code:    137
```

**Fix:** Increase memory limit
```yaml
resources:
  limits:
    memory: "512Mi"  # Increase from 256Mi
  requests:
    memory: "256Mi"
```

**Step 6: Check Image Pull Issues**
```bash
kubectl describe pod myapp-7d8f9c-k2p4x | grep -A 5 "Events"
```

**Problem:** Image pull failed
```
Failed to pull image "myregistry.com/myapp:v1.0": rpc error: code = Unknown desc = Error response from daemon: pull access denied
```

**Fix:**
- Create ImagePullSecret
- Check image name/tag is correct
- Verify registry authentication

**Step 7: Execute into Pod (if running briefly)**
```bash
# If pod runs for a few seconds before crashing
# Quickly exec in to debug
kubectl exec -it myapp-7d8f9c-k2p4x -- /bin/sh

# Inside container:
ls -la /app          # Check files exist
env | sort           # Check environment variables
curl localhost:8080  # Test app manually
```

**Step 8: Check Pod Security/Permissions**
```bash
# Some apps fail if running as non-root but need root permissions
kubectl describe pod myapp-7d8f9c-k2p4x | grep "Security Context" -A 5
```

**Real-World Troubleshooting Example:**

```bash
# Step 1: Identify issue
$ kubectl get pods
NAME                    READY   STATUS             RESTARTS   AGE
api-server-abc123       0/1     CrashLoopBackOff   8          15m

# Step 2: Check events
$ kubectl describe pod api-server-abc123
...
Events:
  Warning  BackOff  2m (x10 over 10m)  kubelet  Back-off restarting failed container

# Step 3: Check logs
$ kubectl logs api-server-abc123 --previous
2024-11-11 10:00:00 INFO: Starting API server...
2024-11-11 10:00:01 ERROR: Failed to connect to database
2024-11-11 10:00:01 ERROR: ECONNREFUSED postgres-service:5432
2024-11-11 10:00:01 FATAL: Cannot start without database connection
Process exited with code 1

# Step 4: Diagnose - connection refused to postgres-service
# Check if postgres service exists
$ kubectl get svc postgres-service
Error from server (NotFound): services "postgres-service" not found

# ROOT CAUSE: Service name wrong or doesn't exist

# Step 5: Check correct service name
$ kubectl get svc | grep postgres
postgres    ClusterIP   10.96.0.10   <none>   5432/TCP   1h

# Service is named "postgres", not "postgres-service"!

# Step 6: Fix deployment
$ kubectl edit deployment api-server
# Change DATABASE_URL from postgres-service:5432 to postgres:5432

# Step 7: Verify fix
$ kubectl get pods
NAME                    READY   STATUS    RESTARTS   AGE
api-server-xyz789       1/1     Running   0          30s

# SUCCESS!
```

**Common Causes of CrashLoopBackOff:**

| Exit Code | Meaning | Common Causes |
|-----------|---------|---------------|
| 0 | Success (but pod exited) | App finished (not long-running), CMD not set |
| 1 | Application error | Uncaught exception, missing config, connection failure |
| 137 | OOMKilled | Out of memory (exceeded limits) |
| 139 | Segmentation fault | Memory corruption, bad binary |
| 255 | Unknown error | General failure |

**Acronym Glossary:**
- **OOM** = Out Of Memory (killed when exceeds memory limit)
- **CMD** = Command (Docker/Kubernetes command to run in container)
- **ConfigMap** = Kubernetes object storing configuration as key-value pairs
- **Secret** = Kubernetes object storing sensitive data (base64 encoded)
- **ClusterIP** = Internal Kubernetes service IP (only accessible inside cluster)
- **Pod** = Smallest deployable unit in Kubernetes (one or more containers)
- **Container** = Running instance of Docker image

**Practical Example:**
```yaml
# Original broken deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api
        image: myregistry.com/api:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "postgres-service:5432"  # WRONG SERVICE NAME
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5  # TOO SHORT (app needs 15s to start)
          periodSeconds: 10
        resources:
          limits:
            memory: "256Mi"  # TOO SMALL (app needs 512Mi)
          requests:
            memory: "128Mi"

# Fixed deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api
        image: myregistry.com/api:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "postgres:5432"  # FIXED: Correct service name
        - name: LOG_LEVEL
          value: "info"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15  # FIXED: Wait longer for startup
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        readinessProbe:  # ADDED: Separate readiness check
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          limits:
            memory: "512Mi"  # FIXED: Increased memory
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
```

**Common Pitfalls:**
1. **Not checking --previous logs:** Current logs might be empty if container just started
2. **Ignoring exit codes:** Exit code 137 = OOM, 1 = app error (different fixes)
3. **Probe timeouts too short:** App needs 30s to start, probe times out at 5s
4. **Missing dependencies:** App needs database, but database pod not ready yet
5. **Wrong image tag:** Using :latest but image wasn't updated
6. **File permissions:** App running as non-root but needs to write to /tmp
7. **ConfigMap not mounted:** App expects config file at /etc/config/app.yaml

**Interview Follow-Up Questions to Expect:**
- "What's the difference between liveness and readiness probes?" (Liveness = restart if fails, readiness = remove from service if fails)
- "What does exit code 137 mean?" (OOMKilled - out of memory)
- "How would you prevent CrashLoopBackOff in the first place?" (Test locally, proper probes, resource limits, health checks)
- "What's ImagePullBackOff vs CrashLoopBackOff?" (ImagePull = can't download image, CrashLoop = image downloaded but container crashes)

---

## Question 2: Python FastAPI Design

**Question:** Design a REST API that handles 10K requests/sec. How do you ensure reliability and performance?

**Feynman Explanation:**
Building a high-traffic API is like designing a highway toll booth. At 10K requests/sec, you can't have one toll booth (single-threaded app) - cars back up for miles. You need multiple lanes (concurrency), E-ZPass lanes (caching), and traffic signals that prevent collisions (rate limiting). You also need emergency lanes (error handling), cameras recording everything (logging), and real-time traffic counts (metrics). FastAPI is like a modern toll plaza with all these features built-in.

**Technical Answer:**

**High-Performance FastAPI Architecture:**

**1. Async Programming (Critical for 10K req/sec)**
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import asyncio
import httpx  # Async HTTP client
from typing import Optional

app = FastAPI()

# WRONG: Blocking I/O (synchronous)
def get_user_sync(user_id: int):
    import requests
    response = requests.get(f"http://user-service/users/{user_id}")  # BLOCKS!
    return response.json()

# RIGHT: Async I/O (non-blocking)
async def get_user_async(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://user-service/users/{user_id}")  # NON-BLOCKING!
        return response.json()

# Async endpoint (can handle many concurrent requests)
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    user = await get_user_async(user_id)  # await = release control while waiting
    return user
```

**Why Async Matters:**
- **Synchronous:** 1 request at a time, 10ms per request = 100 req/sec max (10K req/sec IMPOSSIBLE)
- **Asynchronous:** 1000 concurrent requests, 10ms per request = 100K req/sec possible

**2. Database Connection Pooling**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Create connection pool (reuse connections, don't create new ones each request)
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@db:5432/mydb",
    pool_size=20,          # 20 persistent connections
    max_overflow=10,       # Up to 30 total if needed
    pool_pre_ping=True,    # Check connection is alive before using
    echo=False             # Don't log all SQL (performance)
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency injection for database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Use in endpoint
@app.get("/orders/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
```

**3. Caching (Redis for Hot Data)**
```python
import aioredis
from fastapi import FastAPI
from typing import Optional
import json

app = FastAPI()

# Initialize Redis connection pool
redis: Optional[aioredis.Redis] = None

@app.on_event("startup")
async def startup_event():
    global redis
    redis = await aioredis.create_redis_pool(
        "redis://redis:6379",
        minsize=5,
        maxsize=20
    )

@app.on_event("shutdown")
async def shutdown_event():
    redis.close()
    await redis.wait_closed()

# Cache-aside pattern
@app.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    # Check cache first
    cache_key = f"product:{product_id}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)  # Cache hit (fast!)

    # Cache miss - query database
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Store in cache (TTL = 5 minutes)
    await redis.setex(cache_key, 300, json.dumps(product.dict()))

    return product
```

**4. Rate Limiting (Prevent Abuse)**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Limit: 100 requests per minute per IP
@app.get("/api/data")
@limiter.limit("100/minute")
async def get_data(request: Request):
    return {"data": "some data"}

# Different limits for different endpoints
@app.post("/api/expensive-operation")
@limiter.limit("10/minute")  # Stricter limit for expensive ops
async def expensive_operation(request: Request):
    # Some expensive computation
    return {"result": "done"}
```

**5. Structured Logging**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_obj["user_id"] = record.user_id
        return json.dumps(log_obj)

# Setup logger
logger = logging.getLogger("myapi")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Middleware to add request ID
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info("Request started", extra={"request_id": request_id, "path": request.url.path})

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info("Request completed", extra={"request_id": request_id, "status": response.status_code})

        return response

app.add_middleware(RequestIDMiddleware)
```

**6. Prometheus Metrics**
```python
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

# Define metrics
request_count = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"]
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path

    with request_duration.labels(method=method, endpoint=path).time():
        response = await call_next(request)

    request_count.labels(
        method=method,
        endpoint=path,
        status=response.status_code
    ).inc()

    return response

# Metrics endpoint (for Prometheus scraping)
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

**7. Error Handling & Circuit Breaker**
```python
from circuitbreaker import circuit

# Circuit breaker for external service calls
@circuit(failure_threshold=5, recovery_timeout=60)
async def call_external_service(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        return response.json()

# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(
        f"HTTP exception: {exc.detail}",
        extra={"request_id": request.state.request_id, "status": exc.status_code}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "request_id": request.state.request_id}
    )

# Global exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.exception(
        "Unhandled exception",
        extra={"request_id": request.state.request_id}
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "request_id": request.state.request_id}
    )
```

**8. Health Checks & Readiness**
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    # Check database connection
    try:
        await db.execute(select(1))
        db_status = "up"
    except Exception:
        db_status = "down"
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Check Redis
    try:
        await redis.ping()
        redis_status = "up"
    except Exception:
        redis_status = "down"
        raise HTTPException(status_code=503, detail="Redis unavailable")

    return {
        "status": "ready",
        "database": db_status,
        "redis": redis_status
    }
```

**Deployment Architecture (10K req/sec):**

```
              [Load Balancer (NGINX/ALB)]
                          |
         +----------------+----------------+
         |                |                |
    [API Pod 1]      [API Pod 2]      [API Pod 3]   (Horizontal scaling)
    (4 workers)      (4 workers)      (4 workers)   (12 workers total)
         |                |                |
         +----------------+----------------+
                          |
              [PostgreSQL Connection Pool]
                     (max 100 connections)
                          |
                   [PostgreSQL]

              [Redis Cache Cluster]
             (Cache hot data, 5min TTL)
```

**Performance Calculations:**
- 3 pods × 4 workers = 12 workers
- Each worker handles ~1000 concurrent requests (async)
- 12 × 1000 = 12,000 concurrent requests
- Avg request time: 50ms (with caching)
- Throughput: 12,000 / 0.05 = 240,000 req/sec theoretical
- Real-world: ~100K req/sec (accounting for database, network latency)
- **Target 10K req/sec = easily achievable**

**Acronym Glossary:**
- **REST** = Representational State Transfer (API architectural style)
- **API** = Application Programming Interface
- **TTL** = Time To Live (cache expiration)
- **req/sec** = Requests per second (throughput metric)
- **JSON** = JavaScript Object Notation (data format)
- **HTTP** = Hypertext Transfer Protocol
- **NGINX** = Web server / reverse proxy
- **ALB** = Application Load Balancer (AWS)
- **SSD** = Solid State Drive

**Practical Example:**
```
Scenario: E-commerce product API

Requirements:
- 10,000 requests/sec
- 99.9% uptime (8.76 hours downtime/year max)
- <100ms response time (p95)
- Handle traffic spikes (Black Friday 3x normal)

Implementation:
1. FastAPI with async/await (non-blocking I/O)
2. 10 Kubernetes pods (auto-scaling 5-20 based on CPU)
3. PostgreSQL with read replicas (writes to primary, reads from replicas)
4. Redis cluster (cache product catalog, 5-minute TTL)
5. CDN for static images (Cloudflare)
6. Prometheus + Grafana (monitoring)
7. Horizontal Pod Autoscaler (scale at 70% CPU)

Results:
- Normal traffic: 10K req/sec with 5 pods
- Black Friday: 30K req/sec with 15 pods (auto-scaled)
- Response time: p50=15ms, p95=45ms, p99=120ms
- Uptime: 99.97% (2.6 hours downtime in first year)
- Cost: $500/month (vs $5K/month for traditional setup)
```

**Common Pitfalls:**
1. **Synchronous I/O:** Using `requests` instead of `httpx` (blocks thread)
2. **No connection pooling:** Creating new DB connection per request (slow!)
3. **Missing rate limiting:** API gets DDoS'ed easily
4. **No caching:** Database overwhelmed with repeated queries
5. **Poor error handling:** One error crashes entire app
6. **No monitoring:** Can't diagnose issues in production
7. **Underprovisioned resources:** Pods OOMKill under load

**Interview Follow-Up Questions to Expect:**
- "What's the difference between async and threading?" (Async = single thread, cooperative multitasking; Threading = OS-managed, preemptive)
- "How do you handle database connection exhaustion?" (Connection pooling + queue requests)
- "When would you use Redis vs local cache?" (Redis = distributed/shared, local = single instance)
- "Explain circuit breaker pattern" (Stop calling failing service, give it time to recover)

---

*[Questions 3-10 continue with GitLab CI/CD, Go Microservices, Snowflake Integration, Azure Services, EntraID Authentication, Helm Charts, AWS Integration, and Observability Stack]*

**Next Steps:**
1. Review Q1-Q2 with hands-on practice
2. Set up local Kubernetes (Docker Desktop or Minikube)
3. Build sample FastAPI application
4. Deploy to Kubernetes and troubleshoot deliberately introduced errors
5. Continue to Q3-Q10 for CI/CD, Go, Cloud topics

**Last Updated:** 2025-11-11
**Role:** DevOps Engineer - Data Operations Systems (T-Mobile)
**Compensation:** $48-56/hr (~$100-117K/year)
