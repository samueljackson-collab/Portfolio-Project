# Runbook: High CPU Usage

## Overview

**Severity**: P1-P2 depending on impact
**Primary Symptoms**: CPU usage >80% sustained, increased response times, request timeouts
**Related ADRs**: [ADR-005: Observability Strategy](../adr/ADR-005-comprehensive-observability-strategy.md)

## Symptoms

- CPU usage consistently above 80%
- Increased API response times (P95 >1s)
- Request timeouts
- Pod restarts due to resource limits
- Autoscaler constantly triggering
- User reports of slow application performance

## Detection

### Monitoring Alerts

**Prometheus Alert:**
```yaml
- alert: HighCPUUsage
  expr: |
    (sum(rate(container_cpu_usage_seconds_total{pod=~"app-.*"}[5m]))
    by (pod) /
    sum(container_spec_cpu_quota{pod=~"app-.*"})
    by (pod)) > 0.8
  for: 5m
  labels:
    severity: warning
    team: platform
  annotations:
    summary: "High CPU usage detected on {{ $labels.pod }}"
    description: "CPU usage is {{ $value | humanizePercentage }}"
```

### Manual Check
```bash
# Check pod CPU usage
kubectl top pods -n production --sort-by=cpu

# Check node CPU usage
kubectl top nodes

# Detailed metrics
kubectl exec -n production <pod-name> -- top -bn1 | head -20
```

## Investigation Steps

### 1. Identify Affected Pods (2 minutes)

```bash
# List pods sorted by CPU usage
kubectl top pods -n production --sort-by=cpu

# Get pod details
kubectl describe pod -n production <pod-name>

# Check pod resource limits
kubectl get pod -n production <pod-name> -o jsonpath='{.spec.containers[*].resources}'
```

### 2. Check Recent Changes (2 minutes)

```bash
# Check recent deployments
kubectl rollout history deployment/app -n production

# Get deployment details
kubectl describe deployment app -n production

# Check recent commits
git log --since="24 hours ago" --oneline --all

# Check recent configuration changes
kubectl diff -f kubernetes/production/
```

### 3. Analyze Application Logs (3 minutes)

```bash
# View recent logs from high-CPU pods
kubectl logs -n production <pod-name> --tail=500

# Filter for errors
kubectl logs -n production <pod-name> --tail=1000 | grep -i error

# Check for warning patterns
kubectl logs -n production <pod-name> --tail=1000 | grep -i "warn\|timeout\|slow"

# Export logs for analysis
kubectl logs -n production <pod-name> --since=1h > cpu-spike-logs.txt
```

### 4. Profile Application (5 minutes)

```bash
# Node.js: Enable profiling
kubectl exec -n production <pod-name> -- \
  kill -SIGUSR1 $(pgrep -f "node.*app.js")

# Take CPU profile
kubectl exec -n production <pod-name> -- \
  node --prof-process isolate-*.log > cpu-profile.txt

# Download profile for analysis
kubectl cp production/<pod-name>:/app/isolate-*.log ./cpu-profile.log

# Python: Use py-spy
kubectl exec -n production <pod-name> -- \
  py-spy top --pid 1 --duration 30

# Java: Thread dump
kubectl exec -n production <pod-name> -- \
  jstack <java-pid> > thread-dump.txt
```

### 5. Check Database Queries (3 minutes)

```bash
# Check for slow queries
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      pid,
      now() - query_start as duration,
      query,
      state
    FROM pg_stat_activity
    WHERE state = 'active'
    AND now() - query_start > interval '1 second'
    ORDER BY duration DESC
    LIMIT 20;"

# Check query statistics
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      query,
      calls,
      total_time,
      mean_time,
      max_time
    FROM pg_stat_statements
    ORDER BY mean_time DESC
    LIMIT 20;"
```

### 6. Monitor Real-Time Metrics (Ongoing)

```bash
# Watch CPU usage
watch -n 2 'kubectl top pods -n production | head -20'

# Prometheus query
curl "http://prometheus:9090/api/v1/query?query=
  rate(container_cpu_usage_seconds_total{pod=~\"app-.*\"}[5m])" | jq .

# Grafana dashboard
# Navigate to: https://grafana/d/cpu-usage-dashboard
```

## Common Causes & Solutions

### 1. Inefficient Database Queries (N+1 Problem)

**Symptoms:**
- High CPU correlates with database queries
- Many sequential database calls
- Logs show repeated similar queries

**Investigation:**
```typescript
// Enable query logging
import { createConnection } from 'typeorm';

const connection = await createConnection({
  // ... config
  logging: true,
  logger: 'advanced-console',
  maxQueryExecutionTime: 1000 // Log slow queries
});
```

**Bad Code:**
```typescript
// N+1 Query Problem
async function getOrdersWithUsers() {
  const orders = await db.orders.findAll();

  for (const order of orders) {
    order.user = await db.users.findById(order.userId); // N queries!
  }

  return orders;
}
```

**Solution:**
```typescript
// Use JOIN to fetch related data in one query
async function getOrdersWithUsers() {
  return db.orders.findAll({
    include: [{
      model: User,
      as: 'user'
    }]
  });
}

// Or use DataLoader for batching
import DataLoader from 'dataloader';

const userLoader = new DataLoader(async (userIds) => {
  const users = await db.users.findAll({
    where: { id: { $in: userIds } }
  });

  return userIds.map(id =>
    users.find(user => user.id === id)
  );
});

async function getOrdersWithUsers() {
  const orders = await db.orders.findAll();

  // Batches all user requests into single query
  for (const order of orders) {
    order.user = await userLoader.load(order.userId);
  }

  return orders;
}
```

### 2. Memory Leaks Causing Garbage Collection

**Symptoms:**
- CPU spikes correlate with memory increase
- Garbage collection logs show frequent full GCs
- Memory usage climbing over time

**Investigation:**
```bash
# Check memory usage
kubectl exec -n production <pod-name> -- \
  ps aux --sort=-%mem | head -10

# Node.js: Check heap usage
kubectl exec -n production <pod-name> -- \
  node -e "console.log(process.memoryUsage())"

# Take heap snapshot
kubectl exec -n production <pod-name> -- \
  node --heapsnapshot-signal=SIGUSR2 app.js &

kill -USR2 $(pgrep node)
```

**Bad Code:**
```typescript
// Event listener not cleaned up (memory leak)
class DataProcessor {
  constructor(private eventBus: EventEmitter) {
    // Creates new listener every time
    eventBus.on('data', this.processData);
  }

  private processData(data: any) {
    // Process data
  }
}

// Global array keeps growing
const cache: any[] = [];

function addToCache(item: any) {
  cache.push(item); // Never cleaned up!
}
```

**Solution:**
```typescript
// Proper cleanup of event listeners
class DataProcessor {
  private handler: (data: any) => void;

  constructor(private eventBus: EventEmitter) {
    this.handler = this.processData.bind(this);
    eventBus.on('data', this.handler);
  }

  cleanup() {
    this.eventBus.off('data', this.handler);
  }

  private processData(data: any) {
    // Process data
  }
}

// Use LRU cache with size limits
import LRU from 'lru-cache';

const cache = new LRU({
  max: 1000, // Max items
  maxAge: 1000 * 60 * 60, // 1 hour TTL
  updateAgeOnGet: true
});

function addToCache(key: string, item: any) {
  cache.set(key, item); // Automatically evicts old items
}
```

### 3. Blocking Event Loop (Synchronous Operations)

**Symptoms:**
- CPU pegged at 100% on single core
- Application becomes unresponsive
- Long running synchronous operations in logs

**Investigation:**
```bash
# Check event loop lag
kubectl logs -n production <pod-name> | grep "event.loop.lag"

# Node.js: Monitor event loop
npm install -g clinic
kubectl exec -n production <pod-name> -- clinic doctor -- node app.js
```

**Bad Code:**
```typescript
// Synchronous file processing blocks event loop
function processLargeFile(filePath: string) {
  const data = fs.readFileSync(filePath, 'utf8'); // BLOCKS!
  const parsed = JSON.parse(data); // BLOCKS!
  return transform(parsed); // BLOCKS!
}

// Synchronous crypto operations
function hashPassword(password: string) {
  return crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512');
}
```

**Solution:**
```typescript
// Use async operations
async function processLargeFile(filePath: string) {
  const data = await fs.promises.readFile(filePath, 'utf8');
  const parsed = JSON.parse(data);
  return transform(parsed);
}

// For CPU-intensive work, use worker threads
import { Worker } from 'worker_threads';

async function processLargeFile(filePath: string) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./file-processor.js', {
      workerData: { filePath }
    });

    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) {
        reject(new Error(`Worker stopped with exit code ${code}`));
      }
    });
  });
}

// Use async crypto
async function hashPassword(password: string) {
  return new Promise((resolve, reject) => {
    crypto.pbkdf2(password, salt, 100000, 64, 'sha512', (err, derivedKey) => {
      if (err) reject(err);
      else resolve(derivedKey.toString('hex'));
    });
  });
}
```

### 4. Infinite Loops or Recursion

**Symptoms:**
- CPU immediately spikes to 100%
- Pod becomes unresponsive
- No response to health checks

**Investigation:**
```bash
# Check for stuck processes
kubectl exec -n production <pod-name> -- \
  ps aux --sort=-pcpu | head -20

# Get stack trace (Node.js)
kubectl exec -n production <pod-name> -- \
  kill -SIGUSR1 $(pgrep node)
```

**Bad Code:**
```typescript
// Infinite loop due to logic error
function processItems(items: any[]) {
  let i = 0;
  while (i < items.length) {
    processItem(items[i]);
    // Forgot to increment i!
  }
}

// Unbounded recursion
function fibonacci(n: number): number {
  return fibonacci(n - 1) + fibonacci(n - 2); // No base case!
}
```

**Solution:**
```typescript
// Add loop counter
function processItems(items: any[]) {
  for (let i = 0; i < items.length; i++) {
    processItem(items[i]);
  }
}

// Add recursion depth limit
function fibonacci(n: number, depth: number = 0): number {
  if (depth > 1000) {
    throw new Error('Maximum recursion depth exceeded');
  }

  if (n <= 1) return n;
  return fibonacci(n - 1, depth + 1) + fibonacci(n - 2, depth + 1);
}

// Or use memoization
const memo = new Map<number, number>();

function fibonacci(n: number): number {
  if (n <= 1) return n;

  if (memo.has(n)) {
    return memo.get(n)!;
  }

  const result = fibonacci(n - 1) + fibonacci(n - 2);
  memo.set(n, result);
  return result;
}
```

### 5. Regular Expression Catastrophic Backtracking

**Symptoms:**
- CPU spike when processing specific input
- Request timeout on certain endpoints
- Regex validation taking seconds

**Investigation:**
```bash
# Check logs for regex-related slowness
kubectl logs -n production <pod-name> | grep -i "validation\|regex"
```

**Bad Code:**
```typescript
// Catastrophic backtracking with nested quantifiers
const badRegex = /^(a+)+$/;

// This input causes exponential time complexity
badRegex.test('aaaaaaaaaaaaaaaaaaaaaaaaaaab'); // Hangs!

// Email validation with backtracking
const emailRegex = /^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})*$/;
```

**Solution:**
```typescript
// Use atomic grouping or possessive quantifiers
const goodRegex = /^a+$/;

// Simplified email validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// For complex validation, use libraries
import validator from 'validator';

function isValidEmail(email: string): boolean {
  return validator.isEmail(email);
}

// Add timeout to regex operations
function safeRegexTest(regex: RegExp, input: string, timeout: number = 1000): boolean {
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      resolve(false);
    }, timeout);

    const result = regex.test(input);
    clearTimeout(timer);
    resolve(result);
  });
}
```

## Mitigation Steps

### Immediate Actions (0-5 minutes)

```bash
# 1. Scale up replicas to distribute load
kubectl scale deployment/app -n production --replicas=12

# 2. Increase CPU limits (if not already maxed)
kubectl set resources deployment/app -n production \
  --limits=cpu=1000m,memory=1Gi \
  --requests=cpu=500m,memory=512Mi

# 3. Enable Horizontal Pod Autoscaler if not active
kubectl autoscale deployment/app -n production \
  --cpu-percent=70 \
  --min=5 \
  --max=20

# 4. If caused by recent deployment, rollback
kubectl rollout undo deployment/app -n production

# 5. Verify rollback
kubectl rollout status deployment/app -n production
```

### If Specific Pods Are Affected (5-10 minutes)

```bash
# Restart high-CPU pods
kubectl delete pod -n production <pod-name> --grace-period=30

# Cordon node if entire node is affected
kubectl cordon <node-name>

# Drain node to move workloads
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Uncordon after pods moved
kubectl uncordon <node-name>
```

### Enable Throttling (If Applicable)

```typescript
// Add rate limiting to expensive endpoints
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 10, // Limit each IP to 10 requests per windowMs
  message: 'Too many requests, please try again later'
});

app.use('/api/expensive-operation', apiLimiter);

// Add request timeout
import timeout from 'connect-timeout';

app.use(timeout('30s'));
app.use((req, res, next) => {
  if (!req.timedout) next();
});
```

## Resolution

### 1. Fix Root Cause

Implement one of the solutions from [Common Causes](#common-causes--solutions) section.

### 2. Test Fix

```bash
# Run load tests locally
npm run test:load -- --target=http://localhost:3000

# Deploy to staging
kubectl apply -f kubernetes/staging/ --namespace=staging

# Run integration tests
npm run test:integration -- --env=staging

# Monitor staging CPU
kubectl top pods -n staging -l app=myapp
```

### 3. Deploy to Production (Gradual Rollout)

```bash
# Deploy with canary strategy
kubectl set image deployment/app app=myapp:v1.2.3 -n production

# Monitor canary pods
watch -n 5 'kubectl top pods -n production -l version=v1.2.3'

# Check error rates
curl "http://prometheus:9090/api/v1/query?query=
  rate(http_request_errors_total{version=\"v1.2.3\"}[5m])"

# If successful, continue rollout
kubectl rollout status deployment/app -n production
```

### 4. Verify Resolution

```bash
# Monitor CPU for 30 minutes
watch -n 10 'kubectl top pods -n production'

# Check application metrics
curl "http://prometheus:9090/api/v1/query?query=
  rate(container_cpu_usage_seconds_total{pod=~\"app-.*\"}[10m])" | jq .

# Verify response times improved
curl "http://prometheus:9090/api/v1/query?query=
  histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[10m]))" | jq .
```

## Prevention

### Code Review Checklist
- [ ] No synchronous I/O operations
- [ ] Database queries use indexes
- [ ] No N+1 query patterns
- [ ] Event listeners are cleaned up
- [ ] Regex patterns tested for performance
- [ ] CPU-intensive work uses worker threads
- [ ] Caching implemented for expensive operations

### Monitoring & Alerts
```yaml
# Add preemptive alerting
- alert: CPUUsageIncreasing
  expr: |
    deriv(container_cpu_usage_seconds_total{pod=~"app-.*"}[10m]) > 0.01
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "CPU usage trending upward"

- alert: CPUThrottling
  expr: |
    rate(container_cpu_cfs_throttled_seconds_total{pod=~"app-.*"}[5m]) > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Container CPU being throttled"
```

### Performance Testing
```bash
# Add CPU profiling to CI/CD
npm run profile

# Load testing
artillery run --target https://staging.example.com load-test.yml

# Monitor during load test
kubectl top pods -n staging --sort-by=cpu
```

### Resource Limits
```yaml
# kubernetes/deployment.yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi
```

## Related Runbooks

- [High Error Rate](./runbook-high-error-rate.md)
- [Database Connection Pool Exhaustion](./runbook-database-connection-pool-exhaustion.md)
- [Incident Response Framework](./incident-response-framework.md)

## Additional Resources

- [Node.js Performance Best Practices](https://nodejs.org/en/docs/guides/simple-profiling/)
- [Kubernetes Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [ADR-004: Multi-Layer Caching Strategy](../adr/ADR-004-multi-layer-caching-strategy.md)

---

**Last Updated**: December 2024
**Tested**: December 2024
**Next Review**: March 2025
