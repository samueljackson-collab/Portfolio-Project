# Runbook: Database Connection Pool Exhaustion

## Overview

**Severity**: P0-P1
**Primary Symptoms**: "Connection pool exhausted" errors, database timeouts, 500 errors
**Related ADRs**: [ADR-002: Database Strategy](../adr/README.md) (planned)

## Symptoms

- Application logs showing "connection pool exhausted" errors
- Slow or failing database queries
- HTTP 500 errors with database connection issues
- Timeouts when connecting to database
- Application unresponsive or degraded performance
- Connection count at or near maximum

## Detection

### Monitoring Alerts

**Prometheus Alert:**
```yaml
- alert: DatabaseConnectionPoolExhaustion
  expr: |
    (database_connections_active / database_connections_max) > 0.9
  for: 5m
  labels:
    severity: critical
    team: database
  annotations:
    summary: "Database connection pool nearly exhausted"
    description: "Connection pool at {{ $value | humanizePercentage }} capacity"

- alert: DatabaseConnectionPoolHighUtilization
  expr: |
    (database_connections_active / database_connections_max) > 0.7
  for: 10m
  labels:
    severity: warning
    team: database
  annotations:
    summary: "High database connection pool utilization"
```

### Manual Check
```bash
# Check current connection count
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT count(*) as total_connections
    FROM pg_stat_activity;"

# Check connections by state
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT state, count(*)
    FROM pg_stat_activity
    GROUP BY state;"

# Check application metrics
curl "http://prometheus:9090/api/v1/query?query=database_connections_active"
```

## Investigation Steps

### 1. Identify Current Connection State (2 minutes)

```bash
# Total connections
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      count(*) as total,
      count(*) FILTER (WHERE state = 'active') as active,
      count(*) FILTER (WHERE state = 'idle') as idle,
      count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
    FROM pg_stat_activity;"

# Connection breakdown by application
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      application_name,
      state,
      count(*) as connections
    FROM pg_stat_activity
    WHERE pid <> pg_backend_pid()
    GROUP BY application_name, state
    ORDER BY connections DESC;"

# Max connections setting
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "SHOW max_connections;"
```

### 2. Identify Long-Running Queries (3 minutes)

```bash
# Find active queries and their duration
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      pid,
      now() - query_start as duration,
      state,
      query
    FROM pg_stat_activity
    WHERE state = 'active'
    AND pid <> pg_backend_pid()
    ORDER BY duration DESC
    LIMIT 20;"

# Find idle connections with open transactions
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      pid,
      now() - xact_start as transaction_duration,
      state,
      query
    FROM pg_stat_activity
    WHERE state = 'idle in transaction'
    AND pid <> pg_backend_pid()
    ORDER BY transaction_duration DESC;"
```

### 3. Check Application Logs (2 minutes)

```bash
# Search for connection errors
kubectl logs -n production deployment/app --tail=1000 | \
  grep -i "connection\|pool\|timeout"

# Count connection errors
kubectl logs -n production deployment/app --since=1h | \
  grep -c "connection pool exhausted"

# Sample recent errors
kubectl logs -n production deployment/app --tail=5000 | \
  grep "ECONNREFUSED\|ETIMEDOUT\|connection"
```

### 4. Check Connection Pool Configuration (2 minutes)

```bash
# View current pool configuration
kubectl get configmap -n production app-config -o yaml | \
  grep -A 10 "database"

# Check environment variables
kubectl exec -n production <pod-name> -- \
  env | grep -i "db\|pool\|connection"
```

## Common Causes & Solutions

### 1. Connection Leaks (Not Releasing Connections)

**Symptoms:**
- Idle connections continuously increasing
- Connections not returned to pool
- "idle in transaction" connections piling up

**Bad Code:**
```typescript
// Connection not released on error
async function getUserData(userId: string) {
  const connection = await pool.getConnection();
  const user = await connection.query(
    'SELECT * FROM users WHERE id = ?',
    [userId]
  );
  connection.release(); // Won't execute if query throws!
  return user;
}

// Transaction not properly closed
async function updateUser(userId: string, data: any) {
  await db.query('BEGIN');
  await db.query('UPDATE users SET ... WHERE id = ?', [userId]);
  // Missing COMMIT or ROLLBACK
}
```

**Solution:**
```typescript
// Always use try-finally
async function getUserData(userId: string) {
  const connection = await pool.getConnection();
  try {
    const user = await connection.query(
      'SELECT * FROM users WHERE id = ?',
      [userId]
    );
    return user;
  } finally {
    connection.release(); // Always executed
  }
}

// Better: Use pool.query() which auto-releases
async function getUserData(userId: string) {
  return pool.query('SELECT * FROM users WHERE id = ?', [userId]);
}

// Proper transaction handling
async function updateUser(userId: string, data: any) {
  const connection = await pool.getConnection();
  try {
    await connection.query('BEGIN');
    await connection.query(
      'UPDATE users SET name = ? WHERE id = ?',
      [data.name, userId]
    );
    await connection.query('COMMIT');
  } catch (error) {
    await connection.query('ROLLBACK');
    throw error;
  } finally {
    connection.release();
  }
}

// Or use ORM transactions
async function updateUser(userId: string, data: any) {
  return db.transaction(async (tx) => {
    await tx.users.update(userId, data);
    // Transaction automatically committed or rolled back
  });
}
```

### 2. Pool Size Too Small

**Symptoms:**
- All connections consistently in use
- High wait time for connections
- Scale correlates with connection exhaustion

**Investigation:**
```typescript
// Monitor pool statistics
pool.on('acquire', () => {
  console.log('Connection acquired', {
    total: pool.totalCount,
    active: pool.activeCount,
    idle: pool.idleCount,
    waiting: pool.waitingCount
  });
});
```

**Solution:**
```typescript
// Calculate appropriate pool size
// Formula: (core_count * 2) + effective_spindle_count
// For cloud DB: Start with 20-50 per app instance

const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,

  // Connection pool sizing
  min: 10,  // Minimum idle connections
  max: 50,  // Maximum total connections

  // Timeouts
  connectionTimeoutMillis: 5000,  // 5 seconds to get connection
  idleTimeoutMillis: 30000,       // Close idle connections after 30s
  maxLifetime: 1800000,           // Max connection lifetime: 30 min

  // Error handling
  allowExitOnIdle: false,

  // Logging
  log: (msg) => console.log('Pool:', msg)
});

// Set database max_connections higher than total app pool size
// If 10 app instances with max=50 each: set max_connections=600+
```

### 3. Long-Running Transactions

**Symptoms:**
- "idle in transaction" connections
- Blocking locks
- Connections held for extended periods

**Bad Code:**
```typescript
// External API call inside transaction
async function processOrder(orderId: string) {
  await db.transaction(async (tx) => {
    const order = await tx.orders.findById(orderId);

    // External API call holds transaction open!
    const payment = await externalPaymentAPI.charge({
      amount: order.amount,
      currency: order.currency
    }); // Takes 3-5 seconds

    await tx.orders.update(orderId, {
      status: 'paid',
      paymentId: payment.id
    });

    // Email sending in transaction!
    await sendEmail(order.userEmail, 'Order confirmed');
  });
}
```

**Solution:**
```typescript
// Minimize transaction scope
async function processOrder(orderId: string) {
  // Read data outside transaction
  const order = await db.orders.findById(orderId);

  // External calls outside transaction
  const payment = await externalPaymentAPI.charge({
    amount: order.amount,
    currency: order.currency
  });

  // Quick transaction only for database updates
  await db.transaction(async (tx) => {
    await tx.orders.update(orderId, {
      status: 'paid',
      paymentId: payment.id,
      paidAt: new Date()
    });
  });

  // Async work after transaction
  await sendEmail(order.userEmail, 'Order confirmed');
}

// Set transaction timeout
await db.transaction(
  async (tx) => {
    // Transaction work
  },
  {
    timeout: 5000 // 5 second timeout
  }
);
```

### 4. Missing Connection Pool in Multi-Process Setup

**Bad Code:**
```typescript
// Creating new pool in each request handler
app.get('/users/:id', async (req, res) => {
  const pool = new Pool({ /* config */ }); // Wrong!
  const user = await pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  res.json(user);
});

// Not sharing pool across worker processes
// cluster.js
const cluster = require('cluster');
if (cluster.isMaster) {
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork(); // Each worker creates own pool
  }
}
```

**Solution:**
```typescript
// Create pool once at application startup
import { Pool } from 'pg';

const pool = new Pool({
  // configuration
  max: 20 // Total for this app instance
});

// Reuse pool across requests
app.get('/users/:id', async (req, res) => {
  const user = await pool.query(
    'SELECT * FROM users WHERE id = $1',
    [req.params.id]
  );
  res.json(user);
});

// With clustering: Use PgBouncer or reduce per-worker pool size
// cluster.js
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
} else {
  // Each worker gets smaller pool
  const pool = new Pool({
    max: Math.ceil(50 / numCPUs) // Divide max among workers
  });
}
```

## Mitigation Steps

### Immediate Actions (0-5 minutes)

```bash
# 1. Kill long-running queries (>5 minutes)
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'active'
    AND now() - query_start > interval '5 minutes'
    AND pid <> pg_backend_pid();"

# 2. Kill idle transactions (>2 minutes)
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'idle in transaction'
    AND now() - state_change > interval '2 minutes'
    AND pid <> pg_backend_pid();"

# 3. Temporarily increase max connections (if possible)
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "ALTER SYSTEM SET max_connections = 300;"

kubectl exec -n production db-proxy -- \
  psql -U postgres -c "SELECT pg_reload_conf();"

# 4. Scale down app to reduce connection pressure
kubectl scale deployment/app -n production --replicas=5

# 5. Restart app pods to reset connection pools
kubectl rollout restart deployment/app -n production
```

### Deploy Connection Pooler (PgBouncer) - If Not Present

```bash
# Deploy PgBouncer
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install pgbouncer bitnami/pgbouncer \
  --namespace production \
  --set postgresql.host=postgres.production.svc.cluster.local \
  --set postgresql.port=5432 \
  --set poolMode=transaction \
  --set defaultPoolSize=25 \
  --set maxClientConnections=1000 \
  --set maxDatabaseConnections=100

# Update app to use PgBouncer
kubectl set env deployment/app -n production \
  DB_HOST=pgbouncer.production.svc.cluster.local \
  DB_PORT=6432
```

### Monitor Connection Recovery

```bash
# Watch connection count
watch -n 5 'kubectl exec -n production db-proxy -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"'

# Monitor application logs
kubectl logs -f -n production deployment/app | grep -i connection
```

## Resolution

### 1. Fix Application Code

Implement solutions from [Common Causes](#common-causes--solutions) section.

### 2. Add Connection Monitoring

```typescript
// connection-monitor.ts
import { Pool } from 'pg';
import { metrics } from './metrics';

export function setupConnectionMonitoring(pool: Pool) {
  // Track connection acquisition
  pool.on('connect', (client) => {
    metrics.increment('db.connections.created');
    console.log('New DB connection created');
  });

  pool.on('acquire', (client) => {
    metrics.gauge('db.connections.active', pool.totalCount);
    metrics.gauge('db.connections.idle', pool.idleCount);
    metrics.gauge('db.connections.waiting', pool.waitingCount);
  });

  pool.on('release', (client) => {
    metrics.increment('db.connections.released');
  });

  pool.on('remove', (client) => {
    metrics.increment('db.connections.removed');
    console.log('DB connection removed from pool');
  });

  pool.on('error', (err, client) => {
    metrics.increment('db.connections.errors');
    console.error('DB connection error:', err);
  });

  // Periodic health check
  setInterval(async () => {
    try {
      await pool.query('SELECT 1');
      metrics.gauge('db.pool.healthy', 1);
    } catch (error) {
      metrics.gauge('db.pool.healthy', 0);
      console.error('Pool health check failed:', error);
    }
  }, 30000); // Every 30 seconds
}
```

### 3. Implement Circuit Breaker

```typescript
// circuit-breaker.ts
import CircuitBreaker from 'opossum';

const options = {
  timeout: 5000, // 5 second timeout
  errorThresholdPercentage: 50,
  resetTimeout: 30000 // Try again after 30 seconds
};

const breaker = new CircuitBreaker(
  async (query: string, params: any[]) => {
    return pool.query(query, params);
  },
  options
);

breaker.fallback(() => {
  // Return cached data or error
  throw new Error('Database circuit breaker open');
});

breaker.on('open', () => {
  console.error('Circuit breaker opened - database unavailable');
  metrics.increment('db.circuit_breaker.opened');
});

breaker.on('halfOpen', () => {
  console.log('Circuit breaker half-open - testing database');
});

breaker.on('close', () => {
  console.log('Circuit breaker closed - database recovered');
  metrics.increment('db.circuit_breaker.closed');
});

export async function query(sql: string, params: any[]) {
  return breaker.fire(sql, params);
}
```

### 4. Optimize Database Configuration

```sql
-- Increase max connections
ALTER SYSTEM SET max_connections = 500;

-- Set connection timeout
ALTER SYSTEM SET statement_timeout = '30s';

-- Enable connection logging
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;

-- Reload configuration
SELECT pg_reload_conf();

-- Verify settings
SHOW max_connections;
SHOW statement_timeout;
```

### 5. Deploy and Verify

```bash
# Deploy updated application
kubectl apply -f kubernetes/production/

# Monitor connections after deployment
watch -n 10 'kubectl exec -n production db-proxy -- \
  psql -U postgres -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"'

# Check for errors
kubectl logs -f -n production deployment/app | grep -i error
```

## Prevention

### Code Review Checklist
- [ ] All database connections properly released
- [ ] Transactions kept short and scoped
- [ ] No external API calls inside transactions
- [ ] Connection pool configuration reviewed
- [ ] Error handling includes connection cleanup
- [ ] Using ORM transactions or try-finally blocks

### Monitoring & Alerts
```yaml
# Add comprehensive connection monitoring
- alert: DatabaseConnectionLeaks
  expr: |
    increase(database_connections_active[1h]) > 100
  labels:
    severity: warning
  annotations:
    summary: "Possible connection leak detected"

- alert: IdleTransactions
  expr: |
    pg_stat_activity_idle_in_transaction_count > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High number of idle transactions"

- alert: ConnectionWaitTime
  expr: |
    histogram_quantile(0.95,
      rate(database_connection_wait_seconds_bucket[5m])
    ) > 1
  labels:
    severity: warning
  annotations:
    summary: "High connection wait time"
```

### Load Testing
```bash
# Test connection pool under load
artillery run --target https://staging.example.com connection-load-test.yml

# Monitor during test
watch -n 2 'kubectl exec -n staging db-proxy -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"'
```

### PgBouncer Configuration
```ini
# pgbouncer.ini
[databases]
portfolio = host=postgres.production.svc.cluster.local port=5432

[pgbouncer]
# Connection pooling mode
pool_mode = transaction

# Maximum connections
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5

# Timeouts
server_idle_timeout = 600
server_lifetime = 3600
server_connect_timeout = 15
query_timeout = 30

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

## Related Runbooks

- [High CPU Usage](./runbook-high-cpu-usage.md)
- [High Error Rate](./runbook-high-error-rate.md)
- [Incident Response Framework](./incident-response-framework.md)

## Additional Resources

- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/usage.html)
- [Node.js pg Pool Best Practices](https://node-postgres.com/features/pooling)

---

**Last Updated**: December 2024
**Tested**: December 2024
**Next Review**: March 2025
