# Production Runbooks & Incident Response

## Table of Contents
1. [Incident Response Framework](#incident-response)
2. [High CPU Usage](#runbook-cpu)
3. [Database Connection Pool Exhaustion](#runbook-db)
4. [High Error Rate](#runbook-errors)
5. [Service Down](#runbook-service-down)
6. [Cache Performance Issues](#runbook-cache)
7. [Disaster Recovery](#runbook-dr)
8. [Data Breach Response](#runbook-breach)

---

## Incident Response Framework <a id="incident-response"></a>

### Severity Levels

| Severity | Description | Response Time | Examples |
|----------|-------------|---------------|----------|
| **P0 - Critical** | Complete service outage | 15 minutes | API down, database unavailable |
| **P1 - High** | Major functionality impaired | 1 hour | Payment processing failing, high error rate |
| **P2 - Medium** | Degraded performance | 4 hours | Slow response times, cache issues |
| **P3 - Low** | Minor issues | 24 hours | UI bugs, non-critical features |

### Incident Response Process

```
1. DETECT → 2. TRIAGE → 3. MITIGATE → 4. RESOLVE → 5. POSTMORTEM
```

#### 1. Detection
- Automated alerts (PagerDuty, Slack)
- User reports
- Monitoring dashboards

#### 2. Triage (5 minutes)
```bash
# Quick health check
kubectl get pods -n production
kubectl top pods -n production

# Check recent deployments
kubectl rollout history deployment/app -n production

# View recent logs
kubectl logs -n production deployment/app --tail=100 --since=10m

# Check metrics
curl https://prometheus/api/v1/query?query=up
```

#### 3. Mitigation
- Rollback if recent deployment
- Scale up resources
- Enable circuit breakers
- Route traffic to healthy instances

#### 4. Resolution
- Fix root cause
- Deploy fix
- Verify restoration
- Monitor for recurrence

#### 5. Postmortem
- Timeline of events
- Root cause analysis
- Action items
- Update runbooks

### Communication Templates

#### Initial Alert
```
🚨 INCIDENT DETECTED - P[0-3]

Service: [service-name]
Impact: [description]
Start Time: [timestamp]
Status: Investigating

War Room: [Zoom/Slack link]
Incident Commander: @[name]
```

#### Status Update
```
📊 INCIDENT UPDATE - [HH:MM]

Current Status: [Investigating/Mitigating/Resolved]
Impact: [current impact]
Actions Taken:
- [action 1]
- [action 2]

Next Steps:
- [step 1]
- [step 2]

ETA: [estimated resolution time]
```

#### Resolution
```
✅ INCIDENT RESOLVED

Duration: [time]
Root Cause: [brief description]
Resolution: [what fixed it]

Postmortem: [link]
```

---

## Runbook: High CPU Usage <a id="runbook-cpu"></a>

### Symptoms
- CPU usage >80% sustained
- Increased response times
- Timeouts on requests

### Investigation Steps

```bash
# 1. Identify which pods have high CPU
kubectl top pods -n production --sort-by=cpu

# 2. Check pod logs for errors
kubectl logs -n production <pod-name> --tail=500

# 3. Get detailed metrics
kubectl exec -n production <pod-name> -- top -bn1

# 4. Check for memory leaks
kubectl exec -n production <pod-name> -- ps aux --sort=-%mem | head

# 5. Review recent code changes
git log --since="1 day ago" --oneline

# 6. Check for infinite loops or inefficient queries
kubectl exec -n production <pod-name> -- node --prof app.js
```

### Common Causes

#### 1. Inefficient Database Query
```typescript
// BAD: N+1 query problem
async function getOrdersWithUsers() {
  const orders = await db.orders.findAll();
  for (const order of orders) {
    order.user = await db.users.findById(order.userId); // N queries!
  }
  return orders;
}

// GOOD: Single query with join
async function getOrdersWithUsers() {
  return db.orders.findAll({
    include: [{ model: User }]
  });
}
```

#### 2. Memory Leak
```typescript
// BAD: Event listener not cleaned up
class Service {
  constructor() {
    eventEmitter.on('data', this.handleData);
  }
}

// GOOD: Proper cleanup
class Service {
  constructor() {
    this.handler = this.handleData.bind(this);
    eventEmitter.on('data', this.handler);
  }

  cleanup() {
    eventEmitter.off('data', this.handler);
  }
}
```

#### 3. Blocking Operations
```typescript
// BAD: Blocking CPU-intensive work
function processLargeFile(data) {
  const result = JSON.parse(data); // Blocks event loop
  return transform(result);
}

// GOOD: Use worker threads
import { Worker } from 'worker_threads';

async function processLargeFile(data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./processor.js');
    worker.postMessage(data);
    worker.on('message', resolve);
    worker.on('error', reject);
  });
}
```

### Mitigation Steps

```bash
# 1. Scale up replicas (immediate relief)
kubectl scale deployment/app -n production --replicas=10

# 2. Set CPU limits to prevent resource starvation
kubectl set resources deployment/app -n production \
  --limits=cpu=500m,memory=512Mi \
  --requests=cpu=200m,memory=256Mi

# 3. Enable HPA if not already
kubectl autoscale deployment/app -n production \
  --cpu-percent=70 \
  --min=3 \
  --max=20

# 4. If recent deployment, rollback
kubectl rollout undo deployment/app -n production

# 5. Restart high-CPU pods (graceful deletion)
kubectl delete pod -n production <pod-name>

# Wait for new pod to start
kubectl wait --for=condition=ready pod -l app=myapp -n production --timeout=120s

# Force deletion only as LAST RESORT (if pod is unresponsive)
# WARNING: Force deletion can cause data corruption!
# kubectl delete pod -n production <pod-name> --force --grace-period=0
```

### Resolution

1. Identify and fix inefficient code
2. Add profiling and monitoring
3. Deploy fix with gradual rollout
4. Monitor CPU usage returns to normal

### Prevention
- [ ] Add CPU profiling to CI/CD
- [ ] Set up alerts for CPU >70% for >5 minutes
- [ ] Regular performance testing
- [ ] Code review checklist includes performance

---

## Runbook: Database Connection Pool Exhaustion <a id="runbook-db"></a>

### Symptoms
- "Connection pool exhausted" errors
- Slow database queries
- Timeouts connecting to database
- HTTP 500 errors with DB connection issues

### Investigation

```bash
# 1. Check current connection count
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Identify slow queries
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT pid, now() - query_start as duration, query
    FROM pg_stat_activity
    WHERE state = 'active'
    ORDER BY duration DESC
    LIMIT 10;"

# 3. Check connection pool metrics
curl http://prometheus:9090/api/v1/query?query=database_connections_active

# 4. View application logs for connection errors
kubectl logs -n production deployment/app --tail=1000 | grep "connection"
```

### Common Causes

#### 1. Connection Leaks
```typescript
// BAD: Connection not released
async function getUserData(userId) {
  const connection = await pool.getConnection();
  const user = await connection.query('SELECT * FROM users WHERE id = ?', [userId]);
  return user; // Connection leaked!
}

// GOOD: Always release connections
async function getUserData(userId) {
  const connection = await pool.getConnection();
  try {
    const user = await connection.query('SELECT * FROM users WHERE id = ?', [userId]);
    return user;
  } finally {
    connection.release(); // Always released
  }
}

// BETTER: Use connection pool with auto-release
async function getUserData(userId) {
  return pool.query('SELECT * FROM users WHERE id = ?', [userId]);
  // Pool handles connection lifecycle
}
```

#### 2. Too Small Connection Pool
```typescript
// Configuration
const pool = new Pool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,

  // Pool size calculation: (core_count * 2) + effective_spindle_count
  // For AWS RDS: Start with 20-50 connections per instance
  min: 10,
  max: 50,

  // Connection timeout
  connectionTimeoutMillis: 3000,
  idleTimeoutMillis: 30000,

  // Retry logic
  maxRetries: 3,
  retryDelay: 1000
});
```

#### 3. Long-Running Transactions
```typescript
// BAD: Long transaction holding connections
async function processOrder(orderId) {
  await db.transaction(async (tx) => {
    const order = await tx.orders.findById(orderId);

    // External API call inside transaction!
    await externalPaymentAPI.charge(order.amount); // 5 seconds

    await tx.orders.update(orderId, { status: 'paid' });
  });
}

// GOOD: Minimize transaction scope
async function processOrder(orderId) {
  const order = await db.orders.findById(orderId);

  // External call outside transaction
  const payment = await externalPaymentAPI.charge(order.amount);

  // Quick transaction
  await db.transaction(async (tx) => {
    await tx.orders.update(orderId, {
      status: 'paid',
      paymentId: payment.id
    });
  });
}
```

### Mitigation

```bash
# 1. Kill long-running queries
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'active'
    AND now() - query_start > interval '5 minutes';"

# 2. Temporarily increase max connections (if possible)
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "ALTER SYSTEM SET max_connections = 200;"

# 3. Scale down application pods to reduce load
kubectl scale deployment/app -n production --replicas=5

# 4. Enable connection pooler (PgBouncer)
helm install pgbouncer bitnami/pgbouncer \
  --set postgresql.host=postgres \
  --set postgresql.port=5432 \
  --set poolMode=transaction

# 5. Restart application pods
kubectl rollout restart deployment/app -n production
```

### Resolution

```typescript
// Add connection pool monitoring
pool.on('connect', () => {
  metrics.increment('db.connections.created');
});

pool.on('acquire', () => {
  metrics.gauge('db.connections.active', pool.totalCount);
  metrics.gauge('db.connections.idle', pool.idleCount);
});

pool.on('remove', () => {
  metrics.increment('db.connections.closed');
});

// Add circuit breaker
const breaker = new CircuitBreaker(async (query) => {
  return pool.query(query);
}, {
  timeout: 5000, // 5 second timeout
  errorThresholdPercentage: 50,
  resetTimeout: 30000 // Try again after 30 seconds
});

breaker.fallback(() => {
  return getCachedData();
});
```

### Prevention
- [ ] Set up connection pool monitoring
- [ ] Alert on >80% pool utilization
- [ ] Regular query performance audits
- [ ] Load testing with realistic traffic
- [ ] Implement read replicas for read-heavy queries

---

## Runbook: High Error Rate <a id="runbook-errors"></a>

### Symptoms
- Error rate >1% of requests
- 5xx errors increasing
- User reports of failures

### Investigation

```bash
# 1. Check error distribution
curl "http://prometheus:9090/api/v1/query?query=
  sum(rate(http_request_errors_total[5m])) by (error_type)"

# 2. Sample recent error logs
kubectl logs -n production deployment/app --tail=500 | grep ERROR

# 3. Check for recent deployments
kubectl rollout history deployment/app -n production

# 4. Verify external service health
curl https://api.stripe.com/v1/health
curl https://api.sendgrid.com/v3/health

# 5. Check dependency status
kubectl get pods -n production
kubectl get endpoints -n production
```

### Common Error Patterns

#### 1. Cascading Failures
```typescript
// BAD: No timeout or circuit breaker
async function getUser(userId: string) {
  const response = await fetch(`http://user-service/users/${userId}`);
  return response.json();
}

// GOOD: Timeout + Circuit Breaker + Fallback
import CircuitBreaker from 'opossum';

const options = {
  timeout: 3000, // 3 second timeout
  errorThresholdPercentage: 50,
  resetTimeout: 30000
};

const breaker = new CircuitBreaker(async (userId: string) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3000);

  const response = await fetch(`http://user-service/users/${userId}`, {
    signal: controller.signal
  });

  clearTimeout(timeout);
  return response.json();
}, options);

breaker.fallback(async (userId: string) => {
  // Return cached data or default
  return cache.get(`user:${userId}`) || { id: userId, name: 'Unknown' };
});

async function getUser(userId: string) {
  return breaker.fire(userId);
}
```

#### 2. Unhandled Promise Rejections
```typescript
// BAD: Unhandled rejection crashes app
app.post('/orders', async (req, res) => {
  const order = await createOrder(req.body); // May throw
  res.json(order);
});

// GOOD: Proper error handling
app.post('/orders', async (req, res, next) => {
  try {
    const order = await createOrder(req.body);
    res.json(order);
  } catch (error) {
    logger.error('Order creation failed', { error, body: req.body });

    if (error instanceof ValidationError) {
      return res.status(400).json({ error: error.message });
    }

    next(error); // Pass to error handler
  }
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });

  res.status(500).json({ error: 'Internal server error' });
});
```

#### 3. Dependency Failures
```typescript
// Retry logic with exponential backoff
import retry from 'async-retry';

async function callExternalAPI(data: any) {
  return retry(
    async (bail) => {
      try {
        const response = await fetch('https://external-api.com/endpoint', {
          method: 'POST',
          body: JSON.stringify(data),
          headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
          if (response.status >= 400 && response.status < 500) {
            // Client error - don't retry
            bail(new Error(`API error: ${response.status}`));
            return;
          }
          throw new Error(`API error: ${response.status}`);
        }

        return response.json();
      } catch (error) {
        logger.warn('External API call failed, retrying', { error });
        throw error;
      }
    },
    {
      retries: 3,
      factor: 2,
      minTimeout: 1000,
      maxTimeout: 10000,
      randomize: true
    }
  );
}
```

### Mitigation

```bash
# 1. If recent deployment, rollback immediately
kubectl rollout undo deployment/app -n production

# 2. Check rollback status
kubectl rollout status deployment/app -n production

# 3. Scale up to handle load
kubectl scale deployment/app -n production --replicas=10

# 4. Enable circuit breakers for failing dependencies
# (Application-level configuration)

# 5. Route traffic away from failing instances
kubectl delete pod <failing-pod-name> -n production
```

### Resolution

1. Fix root cause in code
2. Add comprehensive error handling
3. Deploy with gradual rollout (canary)
4. Monitor error rate returns to baseline

### Prevention
- [ ] Implement circuit breakers for all external calls
- [ ] Add retry logic with exponential backoff
- [ ] Set up error rate alerts (<1%)
- [ ] Regular chaos engineering exercises
- [ ] Comprehensive integration testing

---

## Runbook: Service Down <a id="runbook-service-down"></a>

### Symptoms
- Service completely unavailable (HTTP 502/503/504)
- Health check endpoints failing
- Zero successful requests
- Load balancer reporting all instances unhealthy

### Investigation Steps

```bash
# 1. Verify service is actually down (not just network issue)
curl -v https://api.example.com/health

# 2. Check pod/container status
kubectl get pods -n production -l app=myapp

# 3. Check recent events
kubectl get events -n production --sort-by='.lastTimestamp' | head -20

# 4. Check pod logs
kubectl logs -n production deployment/app --tail=100

# 5. Check resource constraints
kubectl describe pod -n production <pod-name> | grep -A5 "Conditions:"

# 6. Check recent deployments
kubectl rollout history deployment/app -n production
```

### Common Causes

#### 1. Application Crash Loop
```bash
# Check pod restart count
kubectl get pods -n production -o wide

# If restarts > 5 in short time, check crash logs
kubectl logs -n production <pod-name> --previous

# Common crash causes:
# - Uncaught exceptions
# - Out of memory
# - Failed health checks
# - Missing environment variables
# - Database connection failures
```

#### 2. Resource Exhaustion
```yaml
# Check if pods are OOMKilled or Evicted
kubectl get pods -n production -o json | jq '.items[] | select(.status.reason=="OOMKilled" or .status.reason=="Evicted")'

# Common resource issues:
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    resources:
      requests:
        memory: "256Mi"  # Too low, app needs 512Mi
        cpu: "100m"
      limits:
        memory: "512Mi"  # App spikes to 600Mi → OOMKilled
        cpu: "500m"
```

#### 3. Failed Deployment
```bash
# Check deployment status
kubectl rollout status deployment/app -n production

# If stuck, describe deployment
kubectl describe deployment app -n production

# Common deployment failures:
# - Image pull errors (wrong tag, auth issues)
# - Configuration errors (invalid ConfigMap/Secret)
# - Readiness probe failures
# - Insufficient cluster resources
```

### Mitigation Steps

```bash
# IMMEDIATE: Rollback to last known good version
kubectl rollout undo deployment/app -n production

# Verify rollback
kubectl rollout status deployment/app -n production
watch kubectl get pods -n production -l app=myapp

# If rollback doesn't work, check previous versions
kubectl rollout history deployment/app -n production
kubectl rollout undo deployment/app -n production --to-revision=5

# If still down, scale to zero and back (last resort)
kubectl scale deployment/app -n production --replicas=0
sleep 10
kubectl scale deployment/app -n production --replicas=3

# Check if service is receiving traffic
kubectl get endpoints -n production

# Manually force restart (deletes pods, deployment recreates)
kubectl delete pod -n production -l app=myapp
```

### Resolution by Cause

#### Scenario A: OOMKilled (Out of Memory)
```bash
# Increase memory limits
kubectl set resources deployment/app -n production \
  --limits=memory=1Gi \
  --requests=memory=512Mi

# Or edit deployment directly
kubectl edit deployment app -n production

# Add memory profiling to identify leak
kubectl exec -n production <pod-name> -- node --inspect --heap-prof app.js
```

#### Scenario B: Image Pull Error
```bash
# Check image pull status
kubectl describe pod -n production <pod-name> | grep -A10 "Events:"

# Common errors:
# - "ImagePullBackOff": Wrong image tag or private registry auth
# - "ErrImageNeverPull": imagePullPolicy preventing download

# Fix by updating image
kubectl set image deployment/app -n production \
  app=myregistry.io/app:v1.2.3

# Or create/update image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=myregistry.io \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=user@example.com \
  -n production
```

#### Scenario C: Database Unreachable
```bash
# Check if app can reach database
kubectl exec -n production <pod-name> -- nc -zv postgres-service 5432

# Check database pod status
kubectl get pods -n production -l app=postgres

# If database is down, restore it first
kubectl rollout restart statefulset/postgres -n production

# Check connection string in app config
kubectl get secret db-config -n production -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Verification

```bash
# 1. Check all pods are running
kubectl get pods -n production -l app=myapp
# All should show "Running" with 1/1 ready

# 2. Test health endpoint
curl https://api.example.com/health
# Should return 200 OK

# 3. Test actual functionality
curl -X POST https://api.example.com/api/test \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# 4. Check error rate in Prometheus
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])"
# Should be near 0

# 5. Monitor for 15 minutes
watch -n 10 'kubectl get pods -n production -l app=myapp'
```

### Prevention
- [ ] Implement proper health checks (liveness + readiness)
- [ ] Set appropriate resource requests/limits
- [ ] Use PodDisruptionBudgets to prevent full outages
- [ ] Implement graceful shutdown handling
- [ ] Test deployments in staging first
- [ ] Use canary deployments for production
- [ ] Set up alerting for pod restarts >3 in 5 minutes

### Escalation
If service remains down after 30 minutes:
1. Engage senior SRE on-call
2. Consider rolling back to previous major version
3. Enable maintenance page
4. Communicate ETA to stakeholders

---

## Runbook: Cache Performance Issues <a id="runbook-cache"></a>

### Symptoms
- Increased database load despite caching layer
- Slow response times on cached endpoints
- Cache hit rate <70%
- Redis/Memcached high CPU or memory usage

### Investigation Steps

```bash
# 1. Check cache hit rate
redis-cli INFO stats | grep keyspace_hits
redis-cli INFO stats | grep keyspace_misses

# Calculate hit rate: hits / (hits + misses)
# Target: >80% for read-heavy workloads

# 2. Check cache memory usage
redis-cli INFO memory

# 3. Check for key evictions
redis-cli INFO stats | grep evicted_keys

# 4. Monitor slow commands
redis-cli SLOWLOG GET 10

# 5. Check connection pool
redis-cli INFO clients | grep connected_clients
```

### Common Causes

#### 1. Cache Stampede (Thundering Herd)
```typescript
// BAD: All requests hit database when cache expires
async function getPopularProduct(productId: string) {
  const cached = await cache.get(`product:${productId}`);
  if (cached) return cached;

  // 1000 concurrent requests all query DB!
  const product = await db.products.findById(productId);
  await cache.set(`product:${productId}`, product, 3600);
  return product;
}

// GOOD: Use locking to prevent stampede
import Redlock from 'redlock';

const redlock = new Redlock([redis], {
  retryCount: 3,
  retryDelay: 200
});

async function getPopularProduct(productId: string) {
  const cacheKey = `product:${productId}`;
  const cached = await cache.get(cacheKey);
  if (cached) return cached;

  // Only one request acquires lock and regenerates cache
  const lockKey = `lock:${cacheKey}`;
  try {
    const lock = await redlock.lock(lockKey, 5000);

    // Double-check cache (another process might have populated it)
    const rechecked = await cache.get(cacheKey);
    if (rechecked) {
      await lock.unlock();
      return rechecked;
    }

    const product = await db.products.findById(productId);
    await cache.set(cacheKey, product, 3600);
    await lock.unlock();
    return product;
  } catch (error) {
    // Lock acquisition failed, query DB directly
    return db.products.findById(productId);
  }
}

// BETTER: Probabilistic early expiration
async function getPopularProduct(productId: string) {
  const cacheKey = `product:${productId}`;
  const cached = await cache.get(cacheKey);

  if (cached) {
    const ttl = await cache.ttl(cacheKey);
    const expiryTime = 3600;
    const beta = 1; // Tuning parameter

    // Probabilistically refresh before expiration
    const shouldRefresh = Math.random() < beta * Math.log(Date.now() / 1000) / ttl;

    if (shouldRefresh) {
      // Refresh in background
      refreshCache(productId).catch(console.error);
    }

    return cached;
  }

  return refreshCache(productId);
}

async function refreshCache(productId: string) {
  const product = await db.products.findById(productId);
  await cache.set(`product:${productId}`, product, 3600);
  return product;
}
```

#### 2. Inefficient Cache Keys (High Cardinality)
```typescript
// BAD: Unique cache key per user
async function getUserFeed(userId: string, page: number, filters: object) {
  // Creates millions of unique keys!
  const key = `feed:${userId}:${page}:${JSON.stringify(filters)}`;
  // ...
}

// GOOD: Limited cardinality, shared cache
async function getUserFeed(userId: string, page: number, filters: object) {
  // Cache feed template (shared across users)
  const feedTemplate = await cache.get(`feed:template:${page}`);

  // Personalize in application layer
  return personalizeFeed(feedTemplate, userId, filters);
}

// Or use cache tags for invalidation
async function cacheWithTags(key: string, data: any, tags: string[]) {
  await cache.set(key, data, 3600);

  // Store reverse index for invalidation
  for (const tag of tags) {
    await cache.sadd(`tag:${tag}`, key);
  }
}

async function invalidateByTag(tag: string) {
  const keys = await cache.smembers(`tag:${tag}`);
  if (keys.length > 0) {
    await cache.del(...keys);
    await cache.del(`tag:${tag}`);
  }
}
```

#### 3. Large Object Storage
```typescript
// BAD: Storing entire object in cache
async function getCatalog() {
  const cached = await cache.get('catalog');
  if (cached) return cached;

  // 50MB catalog object → slow serialization, network transfer
  const catalog = await db.products.findAll({ include: ['images', 'reviews', 'variants'] });
  await cache.set('catalog', catalog, 3600);
  return catalog;
}

// GOOD: Cache only necessary fields
async function getCatalog() {
  const cached = await cache.get('catalog:summary');
  if (cached) return cached;

  // 500KB summary → 100x faster
  const catalog = await db.products.findAll({
    attributes: ['id', 'name', 'price', 'thumbnail']
  });
  await cache.set('catalog:summary', catalog, 3600);
  return catalog;
}

// BETTER: Cache at multiple granularities
async function getProduct(productId: string, detail: 'summary' | 'full' = 'summary') {
  const cacheKey = `product:${productId}:${detail}`;
  const cached = await cache.get(cacheKey);
  if (cached) return cached;

  if (detail === 'summary') {
    const product = await db.products.findById(productId, {
      attributes: ['id', 'name', 'price']
    });
    await cache.set(cacheKey, product, 3600);
    return product;
  } else {
    const product = await db.products.findById(productId, {
      include: ['images', 'reviews', 'variants']
    });
    await cache.set(cacheKey, product, 1800); // Shorter TTL for larger objects
    return product;
  }
}
```

### Mitigation Steps

```bash
# 1. Check for hotkeys (keys with disproportionate access)
redis-cli --hotkeys

# 2. Increase cache memory (temporary)
redis-cli CONFIG SET maxmemory 4gb

# 3. Change eviction policy if needed
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Available policies:
# - allkeys-lru: Evict least recently used keys
# - allkeys-lfu: Evict least frequently used keys
# - volatile-ttl: Evict keys with shortest TTL
# - volatile-lru: LRU among keys with expiration

# 4. Clear problematic keys
redis-cli KEYS 'bad-pattern:*' | xargs redis-cli DEL

# 5. Restart cache if memory fragmentation high
redis-cli INFO memory | grep mem_fragmentation_ratio
# If >1.5, consider restart
```

### Resolution

```typescript
// Monitor cache performance
import { createClient } from 'redis';

const redis = createClient();

// Track cache hits/misses
async function getCached<T>(key: string, fallback: () => Promise<T>, ttl: number): Promise<T> {
  const start = Date.now();
  const cached = await redis.get(key);

  if (cached) {
    metrics.increment('cache.hit');
    metrics.timing('cache.latency', Date.now() - start);
    return JSON.parse(cached);
  }

  metrics.increment('cache.miss');
  const data = await fallback();
  await redis.setex(key, ttl, JSON.stringify(data));
  metrics.timing('cache.miss.latency', Date.now() - start);

  return data;
}

// Implement cache warming for predictable load
async function warmCache() {
  const popularProducts = await db.products.findAll({
    where: { views: { $gt: 1000 } },
    attributes: ['id']
  });

  for (const product of popularProducts) {
    await getProduct(product.id); // Populates cache
  }

  logger.info(`Warmed cache with ${popularProducts.length} products`);
}

// Run cache warming on deployment
if (process.env.NODE_ENV === 'production') {
  warmCache().catch(logger.error);
}
```

### Verification

```bash
# 1. Check cache hit rate improved
redis-cli INFO stats | grep keyspace_hits
redis-cli INFO stats | grep keyspace_misses

# 2. Monitor database query rate decreased
# Should see 30-50% reduction in DB queries

# 3. Check response times improved
curl -w "@curl-format.txt" https://api.example.com/products

# 4. Monitor for 24 hours to ensure stability
watch -n 60 'redis-cli INFO stats | grep -E "hits|misses|evicted"'
```

### Prevention
- [ ] Set up cache hit rate monitoring (alert if <70%)
- [ ] Implement cache key naming conventions
- [ ] Document cache TTL strategies per data type
- [ ] Regular cache performance reviews
- [ ] Load testing with realistic cache scenarios
- [ ] Implement cache versioning for safe invalidation

---

## Runbook: Disaster Recovery <a id="runbook-dr"></a>

### Scenarios
1. Complete region failure (AWS us-east-1 down)
2. Database corruption
3. Security breach requiring complete rebuild

### Recovery Time Objective (RTO): 15 minutes
### Recovery Point Objective (RPO): 5 minutes

### Pre-Requisites
- [x] DR region configured (us-west-2)
- [x] Database replication active
- [x] Automated backups running
- [x] DR runbook tested monthly
- [x] Access credentials secured

### DR Procedure: Region Failover

```bash
#!/bin/bash
# dr-failover.sh - Execute region failover

set -e

echo "=== DISASTER RECOVERY FAILOVER ==="
echo "Primary Region: us-east-1"
echo "DR Region: us-west-2"
echo ""
read -p "Are you sure you want to proceed? (type YES): " confirm

if [ "$confirm" != "YES" ]; then
  echo "Failover cancelled"
  exit 1
fi

# 1. Update DNS to point to DR region
echo "Step 1: Updating Route53 DNS..."
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z0987654321XYZ",
          "DNSName": "dr-lb.us-west-2.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# 2. Promote RDS read replica to master
echo "Step 2: Promoting read replica to master..."
aws rds promote-read-replica \
  --db-instance-identifier portfolio-dr-replica \
  --region us-west-2

# Wait for promotion
aws rds wait db-instance-available \
  --db-instance-identifier portfolio-dr-replica \
  --region us-west-2

# 3. Update application configuration
echo "Step 3: Updating application configuration..."
kubectl config use-context dr-cluster

# Retrieve database credentials from AWS Secrets Manager
DB_URL=$(aws secretsmanager get-secret-value \
  --secret-id dr-database-url \
  --region us-west-2 \
  --query SecretString \
  --output text | jq -r .DATABASE_URL)

kubectl set env deployment/app -n production \
  DATABASE_URL="$DB_URL"

# 4. Scale up DR environment
echo "Step 4: Scaling up DR environment..."
kubectl scale deployment/app -n production --replicas=10

# 5. Verify health
echo "Step 5: Verifying application health..."
for i in {1..30}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)
  if [ "$status" = "200" ]; then
    echo "✓ Application healthy in DR region"
    break
  fi
  echo "Waiting for application... ($i/30)"
  sleep 2
done

# 6. Enable monitoring in DR region
echo "Step 6: Enabling monitoring..."
kubectl apply -f monitoring/dr-alerts.yaml

# 7. Notify team
echo "Step 7: Sending notifications..."
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -d '{
    "channel": "#incidents",
    "text": "🚨 DR FAILOVER COMPLETE\nRegion: us-west-2\nStatus: ACTIVE\nTime: '$(date)'"
  }'

echo ""
echo "=== FAILOVER COMPLETE ==="
echo "Primary Region: us-west-2 (DR)"
echo "Status: ACTIVE"
echo "Next Steps:"
echo "1. Monitor application metrics"
echo "2. Investigate primary region failure"
echo "3. Schedule failback when primary is restored"
```

### Database Recovery

```bash
# Restore from point-in-time backup
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier portfolio-prod \
  --target-db-instance-identifier portfolio-restored \
  --restore-time 2024-12-15T10:30:00Z

# Or restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier portfolio-restored \
  --db-snapshot-identifier portfolio-snapshot-2024-12-15

# Verify data integrity
psql -h restored-db.amazonaws.com -U postgres -d portfolio -c "
  SELECT
    COUNT(*) as total_records,
    MAX(created_at) as latest_record,
    MIN(created_at) as earliest_record
  FROM orders;"
```

### Application State Recovery

```bash
# Restore Redis cache from backup
redis-cli --rdb /backup/redis-dump-2024-12-15.rdb

# Restore application configuration
kubectl apply -f backup/configmaps-2024-12-15.yaml
kubectl apply -f backup/secrets-2024-12-15.yaml

# Restore persistent volumes
kubectl apply -f backup/pv-snapshots-2024-12-15.yaml
```

### Post-Recovery Validation

```bash
# Run smoke tests
npm run test:smoke -- --env=production

# Verify critical flows
curl -X POST https://api.example.com/test/orders \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check data consistency
psql -h db.amazonaws.com -U postgres -d portfolio -c "
  SELECT
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM orders) as orders,
    (SELECT COUNT(*) FROM products) as products;"

# Monitor error rates
curl "http://prometheus:9090/api/v1/query?query=
  rate(http_request_errors_total[5m])"
```

### Failback Procedure

```bash
#!/bin/bash
# dr-failback.sh - Return to primary region

echo "=== FAILBACK TO PRIMARY REGION ==="

# 1. Verify primary region is healthy
echo "Step 1: Verifying primary region health..."
kubectl config use-context primary-cluster
kubectl get nodes
kubectl get pods -n production

# 2. Sync data from DR to primary
echo "Step 2: Syncing database..."
pg_dump -h dr-db.us-west-2.amazonaws.com -U postgres portfolio | \
  psql -h primary-db.us-east-1.amazonaws.com -U postgres portfolio

# 3. Update DNS back to primary
echo "Step 3: Updating DNS to primary..."
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z1234567890ABC",
          "DNSName": "primary-lb.us-east-1.elb.amazonaws.com"
        }
      }
    }]
  }'

# 4. Scale up primary
kubectl scale deployment/app -n production --replicas=10

# 5. Scale down DR (keep warm standby)
kubectl config use-context dr-cluster
kubectl scale deployment/app -n production --replicas=2

echo "=== FAILBACK COMPLETE ==="
```

---

## Security Incident Response <a id="runbook-breach"></a>

### Incident Types
- Data breach
- Unauthorized access
- DDoS attack
- Malware/ransomware
- Insider threat

### Immediate Response (First 15 Minutes)

```bash
# 1. Isolate affected systems
kubectl cordon <affected-node>
kubectl drain <affected-node> --ignore-daemonsets

# 2. Preserve evidence
kubectl logs <affected-pod> > evidence-$(date +%Y%m%d-%H%M%S).log
kubectl get events --sort-by='.lastTimestamp' > events-$(date +%Y%m%d-%H%M%S).log

# 3. Revoke compromised credentials
aws iam update-access-key \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Inactive

# 4. Enable enhanced logging
kubectl apply -f enhanced-audit-policy.yaml

# 5. Notify security team
curl -X POST $SLACK_WEBHOOK -d '{
  "text": "🚨 SECURITY INCIDENT\nType: Data Breach\nSeverity: P0\nTime: '$(date)'",
  "channel": "#security-incidents"
}'
```

### Investigation Checklist

- [ ] Identify attack vector
- [ ] Determine scope of compromise
- [ ] List affected systems and data
- [ ] Preserve forensic evidence
- [ ] Review access logs
- [ ] Check for lateral movement
- [ ] Identify data exfiltration
- [ ] Document timeline

### Containment

```bash
# Rotate all secrets
kubectl delete secret --all -n production
kubectl create secret generic api-keys --from-literal=...

# Force password reset for all users
psql -h db.amazonaws.com -U postgres -d portfolio -c "
  UPDATE users
  SET password_reset_required = true,
      reset_token = gen_random_uuid(),
      reset_token_expires = NOW() + INTERVAL '24 hours';"

# Block suspicious IPs
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-suspicious-ips
spec:
  podSelector:
    matchLabels:
      app: portfolio
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 192.0.2.0/24  # Suspicious IP range
EOF
```

### Recovery

1. Patch vulnerabilities
2. Update all credentials
3. Re-deploy from clean source
4. Verify no backdoors remain
5. Enable additional monitoring
6. Conduct security audit

### Legal & Compliance

```markdown
## Notification Requirements

### GDPR (EU customers)
- Notify within 72 hours of discovery
- Include: nature of breach, affected data, mitigation steps
- Contact: DPA@example.com

### CCPA (California residents)
- Notify without unreasonable delay
- Include: types of information compromised
- Contact: legal@example.com

### PCI DSS (payment data)
- Notify immediately
- Contact: acquiring bank, card brands
- Forensic investigation required
```

### Post-Incident Actions

- [ ] Complete postmortem
- [ ] Update security policies
- [ ] Conduct security training
- [ ] Implement additional controls
- [ ] Test incident response plan
- [ ] Review insurance coverage
- [ ] Public disclosure (if required)

---

## Performance Optimization Runbook

### Slow API Response Times

```bash
# 1. Identify slow endpoints
curl "http://prometheus:9090/api/v1/query?query=
  histogram_quantile(0.95,
    rate(http_request_duration_seconds_bucket[5m])
  ) by (endpoint)" | jq .

# 2. Enable detailed tracing
kubectl set env deployment/app -n production \
  OTEL_TRACES_SAMPLER=always_on

# 3. Analyze database queries
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT query,
           mean_exec_time,
           calls
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT 20;"

# 4. Check for N+1 queries
# (Review application logs and traces)

# 5. Add database indexes if needed
kubectl exec -n production db-proxy -- \
  psql -U postgres -d portfolio -c "
    CREATE INDEX CONCURRENTLY idx_orders_user_id
    ON orders(user_id);"
```

### Memory Leaks

```bash
# 1. Take heap snapshot
kubectl exec -n production <pod-name> -- \
  node --inspect --heapsnapshot-signal=SIGUSR2 app.js &

# Send signal to take snapshot
kubectl exec -n production <pod-name> -- kill -USR2 $(pgrep node)

# 2. Download snapshot
kubectl cp production/<pod-name>:/app/heap.snapshot ./heap.snapshot

# 3. Analyze with Chrome DevTools
# Open chrome://inspect and load snapshot

# 4. Identify memory leaks
# Look for retained objects, event listeners, timers
```

### Common Memory Leak Patterns

```typescript
// BAD: Global variable accumulation
let requestCache = []; // Grows indefinitely

app.get('/api/data', (req, res) => {
  requestCache.push({ timestamp: Date.now(), data: req.body });
  res.json({ success: true });
});

// GOOD: Use bounded cache
import LRU from 'lru-cache';

const requestCache = new LRU({
  max: 500, // Maximum 500 items
  maxAge: 1000 * 60 * 60 // 1 hour TTL
});

app.get('/api/data', (req, res) => {
  requestCache.set(Date.now(), req.body);
  res.json({ success: true });
});
```

```typescript
// BAD: Event listeners not removed
class DataService {
  constructor() {
    eventBus.on('data', this.handleData); // Leak!
  }

  handleData(data) {
    // Process data
  }
}

// GOOD: Clean up event listeners
class DataService {
  private handler: (data: any) => void;

  constructor() {
    this.handler = this.handleData.bind(this);
    eventBus.on('data', this.handler);
  }

  handleData(data) {
    // Process data
  }

  destroy() {
    eventBus.off('data', this.handler);
  }
}
```

```typescript
// BAD: Timers not cleared
class PollingService {
  start() {
    setInterval(() => {
      this.poll();
    }, 5000); // Never cleared!
  }

  poll() {
    // Fetch data
  }
}

// GOOD: Track and clear timers
class PollingService {
  private intervalId?: NodeJS.Timeout;

  start() {
    this.intervalId = setInterval(() => {
      this.poll();
    }, 5000);
  }

  poll() {
    // Fetch data
  }

  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }
}
```

```typescript
// BAD: Closures retaining large objects
function createHandlers(largeDataset) {
  return {
    process: () => {
      // Closure captures entire largeDataset (10MB)
      return largeDataset.filter(x => x.active);
    }
  };
}

// GOOD: Extract only needed data
function createHandlers(largeDataset) {
  // Extract only IDs (100KB)
  const activeIds = largeDataset
    .filter(x => x.active)
    .map(x => x.id);

  return {
    process: () => {
      // Closure only captures activeIds
      return activeIds;
    }
  };
}
```

### Database Query Optimization

```sql
-- BAD: Full table scan
SELECT * FROM orders
WHERE customer_email = 'user@example.com';

-- GOOD: Use index
CREATE INDEX idx_orders_customer_email ON orders(customer_email);

-- BAD: Inefficient join
SELECT o.*, u.*, p.*
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
WHERE o.created_at > NOW() - INTERVAL '30 days';

-- GOOD: Filter early, select specific columns
SELECT o.id, o.amount, u.email, p.name
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
WHERE o.created_at > NOW() - INTERVAL '30 days'
  AND o.status = 'completed'
LIMIT 100;

-- BAD: N+1 query in application
-- Application code:
-- orders.forEach(order => {
--   order.user = await db.users.findById(order.user_id);
-- });

-- GOOD: Single query with JOIN or IN clause
SELECT o.*, u.email, u.name
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```

---

**End of Production Runbooks & Incident Response**

*Last Updated: 2025-11-10*
*Version: 1.0*
*Maintainer: Portfolio Project*
*Next Review: 2026-02-10 (Quarterly)*
