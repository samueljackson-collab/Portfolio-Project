# Runbook: High Error Rate

## Overview

**Severity**: P0-P1
**Primary Symptoms**: Error rate >1%, 5xx errors increasing, user reports of failures
**Related ADRs**: [ADR-005: Observability Strategy](../adr/ADR-005-comprehensive-observability-strategy.md), [ADR-007: Event-Driven Architecture](../adr/ADR-007-event-driven-architecture.md)

## Symptoms

- Error rate >1% of total requests
- 5xx HTTP status codes increasing
- User reports of failures or unexpected behavior
- Failed requests in logs
- Circuit breakers opening
- Dependency failures

## Detection

### Monitoring Alerts

```yaml
- alert: HighErrorRate
  expr: |
    (sum(rate(http_request_errors_total[5m]))
    / sum(rate(http_requests_total[5m]))) > 0.01
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value | humanizePercentage }}"

- alert: 5xxErrors
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m])) > 10
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High number of 5xx errors"
```

## Investigation Steps

### 1. Identify Error Distribution (2 minutes)

```bash
# Check error count by endpoint
curl "http://prometheus:9090/api/v1/query?query=
  sum(rate(http_request_errors_total[5m])) by (endpoint, error_type)" | jq .

# Check status code distribution
kubectl logs -n production deployment/app --tail=1000 | \
  grep -oP '(?<=status:)\d{3}' | sort | uniq -c | sort -rn

# Sample recent errors
kubectl logs -n production deployment/app --tail=500 | grep ERROR
```

### 2. Check Recent Deployments (2 minutes)

```bash
# Check rollout history
kubectl rollout history deployment/app -n production

# Get latest deployment details
kubectl describe deployment app -n production | grep -A 10 "Events:"

# Check recent commits
git log --since="2 hours ago" --oneline
```

### 3. Verify External Dependencies (3 minutes)

```bash
# Check database connectivity
kubectl exec -n production db-proxy -- psql -U postgres -c "SELECT 1"

# Test external APIs
curl -I https://api.stripe.com/v1/health
curl -I https://api.sendgrid.com/v3/health

# Check service mesh status
kubectl get pods -n production -l app=istio
```

## Common Causes & Solutions

### 1. Cascading Failures

**Bad Code:**
```typescript
// No timeout or circuit breaker
async function getUserProfile(userId: string) {
  const response = await fetch(`http://user-service/users/${userId}`);
  return response.json();
}
```

**Solution:**
```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(
  async (userId: string) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    try {
      const response = await fetch(
        `http://user-service/users/${userId}`,
        { signal: controller.signal }
      );
      clearTimeout(timeout);
      return response.json();
    } catch (error) {
      clearTimeout(timeout);
      throw error;
    }
  },
  {
    timeout: 3000,
    errorThresholdPercentage: 50,
    resetTimeout: 30000
  }
);

breaker.fallback(async (userId: string) => {
  return cache.get(`user:${userId}`) || { id: userId, name: 'Unknown' };
});

async function getUserProfile(userId: string) {
  return breaker.fire(userId);
}
```

### 2. Unhandled Exceptions

**Bad Code:**
```typescript
app.post('/orders', async (req, res) => {
  const order = await createOrder(req.body); // May throw
  res.json(order);
});
```

**Solution:**
```typescript
// Add error handling middleware
app.post('/orders', async (req, res, next) => {
  try {
    const order = await createOrder(req.body);
    res.json(order);
  } catch (error) {
    logger.error('Order creation failed', { error, body: req.body });

    if (error instanceof ValidationError) {
      return res.status(400).json({ error: error.message });
    }

    next(error);
  }
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    path: req.path
  });

  res.status(500).json({ error: 'Internal server error' });
});
```

### 3. Dependency Failures with Retry Logic

**Solution:**
```typescript
import retry from 'async-retry';

async function callExternalAPI(data: any) {
  return retry(
    async (bail) => {
      try {
        const response = await fetch('https://external-api.com/endpoint', {
          method: 'POST',
          body: JSON.stringify(data)
        });

        if (!response.ok) {
          if (response.status >= 400 && response.status < 500) {
            bail(new Error(`Client error: ${response.status}`));
            return;
          }
          throw new Error(`Server error: ${response.status}`);
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

## Mitigation Steps

### Immediate Actions (0-5 minutes)

```bash
# 1. Check if recent deployment caused issue
kubectl rollout history deployment/app -n production

# 2. If recent deployment, rollback immediately
kubectl rollout undo deployment/app -n production

# 3. Verify rollback
kubectl rollout status deployment/app -n production

# 4. Scale up to handle load
kubectl scale deployment/app -n production --replicas=10

# 5. Enable circuit breakers (if not already)
kubectl set env deployment/app -n production \
  CIRCUIT_BREAKER_ENABLED=true
```

### Route Traffic Away from Failing Instances

```bash
# Identify failing pods
kubectl get pods -n production -l app=myapp

# Delete specific failing pods
kubectl delete pod <failing-pod-name> -n production

# Or drain entire node
kubectl drain <node-name> --ignore-daemonsets
```

## Resolution

### 1. Fix Root Cause

Deploy code fixes using gradual rollout:

```bash
# Deploy with canary
kubectl set image deployment/app app=myapp:v1.2.3 -n production --record

# Monitor canary error rate
watch -n 5 'kubectl logs -n production -l version=v1.2.3 | grep -c ERROR'

# If successful, continue rollout
kubectl rollout resume deployment/app -n production
```

### 2. Verify Resolution

```bash
# Monitor error rate for 30 minutes
curl "http://prometheus:9090/api/v1/query?query=
  rate(http_request_errors_total[10m])" | jq .

# Check logs
kubectl logs -n production deployment/app --tail=100 | grep -c ERROR
```

## Prevention

### Error Handling Best Practices

```typescript
// 1. Use async error handling
app.use(asyncHandler(async (req, res) => {
  // Automatically catches async errors
}));

// 2. Validate input
import Joi from 'joi';

const schema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required()
});

app.post('/register', async (req, res) => {
  const { error, value } = schema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.message });
  }
  // Process valid data
});

// 3. Implement retries and fallbacks
// 4. Add comprehensive logging
// 5. Use circuit breakers
```

## Related Runbooks

- [High CPU Usage](./runbook-high-cpu-usage.md)
- [Database Connection Pool Exhaustion](./runbook-database-connection-pool-exhaustion.md)
- [Incident Response Framework](./incident-response-framework.md)

---

**Last Updated**: December 2024
**Tested**: December 2024
**Next Review**: March 2025
