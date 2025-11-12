# Runbook — Project 15 (Real-time Collaborative Platform)

## Overview

Production operations runbook for Real-time Collaborative Platform. This runbook covers WebSocket gateway operations, Operational Transform (OT) engine management, CRDT reconciliation, presence tracking, JWT authentication, and monitoring for low-latency collaborative document editing.

**System Components:**
- WebSocket gateway (real-time connections)
- Operational Transform (OT) engine (conflict resolution)
- CRDT reconciliation (offline sync)
- Document queue manager (per-document operation queues)
- Presence service (user activity tracking)
- JWT authentication service
- Redis (operation cache and presence data)
- PostgreSQL (document persistence)
- Load balancer (WebSocket distribution)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Operation latency (p95)** | < 50ms | Time from operation submit → broadcast |
| **WebSocket uptime** | 99.9% | Connection availability |
| **Concurrent users** | Support 10,000+ | Active WebSocket connections |
| **Conflict resolution time** | < 10ms | OT transformation time |
| **Document sync success** | 99.99% | Successful CRDT reconciliations |
| **Presence update latency** | < 200ms | Cursor/selection updates |
| **Authentication latency** | < 100ms | JWT validation time |

---

## Dashboards & Alerts

### Dashboards

#### Connection Health Dashboard
```bash
# Check WebSocket gateway status
curl -f http://localhost:8080/health

# Check active connections
curl -s http://localhost:8080/api/metrics/connections | \
  jq '{total_connections, active_users, documents_open}'

# Check connection distribution across servers
for server in collab-{01..04}.example.com; do
  echo "=== $server ==="
  curl -s http://$server:8080/api/metrics/connections | \
    jq '{connections: .total_connections}'
done

# Check Redis connection pool
redis-cli INFO | grep -E "connected_clients|blocked_clients"

# Check WebSocket errors
tail -100 logs/websocket.log | grep -c ERROR
```

#### Document Activity Dashboard
```bash
# List active documents
curl -s http://localhost:8080/api/documents/active | \
  jq '.documents[] | {id, title, users, operations_per_min}'

# Check specific document activity
DOC_ID="doc-12345"
curl -s http://localhost:8080/api/documents/$DOC_ID/activity | \
  jq '{users, pending_operations, last_update}'

# Check operation queue depths
curl -s http://localhost:8080/api/metrics/queues | \
  jq '.queues[] | {document_id, depth, processing_rate}'

# View recent operations
redis-cli LRANGE "operations:doc-12345" 0 10
```

#### Presence and Collaboration
```bash
# Check active users
curl -s http://localhost:8080/api/presence/users | \
  jq '.users[] | {user_id, document_id, last_activity}'

# Check presence broadcast latency
curl -s http://localhost:8080/api/metrics/presence | \
  jq '{broadcast_latency_ms, updates_per_second}'

# View user cursors/selections
curl -s http://localhost:8080/api/presence/document/$DOC_ID | \
  jq '.cursors'

# Check awareness states
curl -s http://localhost:8080/api/presence/awareness | \
  jq '{active_users, idle_users, disconnected_users}'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | WebSocket gateway down | Immediate | Restart gateway, check load balancer |
| **P0** | All operations failing | Immediate | Check OT engine, Redis, database |
| **P0** | Data loss detected | Immediate | Enable CRDT recovery, investigate |
| **P1** | High operation latency (>200ms) | 15 minutes | Scale workers, check Redis |
| **P1** | Conflict resolution failures | 30 minutes | Review OT logic, check document state |
| **P1** | WebSocket connections dropping | 30 minutes | Check network, increase timeout |
| **P2** | Presence updates delayed | 1 hour | Check presence service, Redis |
| **P2** | Queue depth growing | 1 hour | Scale processing, optimize operations |
| **P3** | Individual connection issues | 4 hours | Review client logs, network |

#### Alert Queries

```bash
# Check operation latency
LATENCY=$(curl -s http://localhost:8080/api/metrics | jq '.operation_latency_p95_ms')
if [ $(echo "$LATENCY > 200" | bc) -eq 1 ]; then
  echo "ALERT: Operation latency is ${LATENCY}ms"
fi

# Check WebSocket gateway health
if ! curl -sf http://localhost:8080/health > /dev/null; then
  echo "ALERT: WebSocket gateway is down"
  exit 1
fi

# Check Redis connectivity
if ! redis-cli ping > /dev/null 2>&1; then
  echo "ALERT: Redis is unreachable"
  exit 1
fi

# Check operation queue depths
MAX_QUEUE=$(curl -s http://localhost:8080/api/metrics/queues | \
  jq '.queues | map(.depth) | max')
if [ "$MAX_QUEUE" -gt 1000 ]; then
  echo "ALERT: Operation queue depth is $MAX_QUEUE"
fi

# Check conflict resolution failures
CONFLICTS=$(curl -s http://localhost:8080/api/metrics | \
  jq '.conflict_resolution_failures_last_hour')
if [ "$CONFLICTS" -gt 10 ]; then
  echo "ALERT: $CONFLICTS conflict resolution failures"
fi

# Check WebSocket connection drops
DROPS=$(curl -s http://localhost:8080/api/metrics | \
  jq '.websocket_disconnections_last_hour')
CONNECTIONS=$(curl -s http://localhost:8080/api/metrics/connections | \
  jq '.total_connections')

if [ $CONNECTIONS -gt 0 ]; then
  DROP_RATE=$(echo "scale=2; $DROPS / $CONNECTIONS * 100" | bc)
  if [ $(echo "$DROP_RATE > 10" | bc) -eq 1 ]; then
    echo "ALERT: WebSocket drop rate is ${DROP_RATE}%"
  fi
fi
```

---

## Standard Operations

### WebSocket Gateway Operations

#### Start/Stop Gateway
```bash
# Start collaboration server
cd /home/user/Portfolio-Project/projects/15-real-time-collaboration
source venv/bin/activate
python src/collaboration_server.py

# Start in production mode
python src/collaboration_server.py \
  --config config/production.yaml \
  --workers 4 \
  --port 8080

# Start as systemd service
sudo systemctl start collaboration-server

# Check status
sudo systemctl status collaboration-server

# Stop server (gracefully)
sudo systemctl stop collaboration-server

# Or send graceful shutdown signal
kill -SIGTERM $(cat collaboration-server.pid)

# View logs
sudo journalctl -u collaboration-server -f
```

#### Configure Gateway
```bash
# Edit configuration
vim config/collaboration_config.yaml

# Example configuration:
cat > config/collaboration_config.yaml << 'EOF'
server:
  host: "0.0.0.0"
  port: 8080
  workers: 4
  max_connections: 10000

websocket:
  ping_interval: 30
  ping_timeout: 10
  max_message_size: 1048576  # 1MB
  compression: true

authentication:
  jwt_secret: ${JWT_SECRET}
  jwt_algorithm: HS256
  token_expiry_seconds: 3600

operational_transform:
  enabled: true
  max_queue_size: 1000
  batch_size: 10
  batch_timeout_ms: 50

crdt:
  enabled: true
  sync_interval_seconds: 60
  conflict_resolution: last_write_wins

redis:
  host: localhost
  port: 6379
  db: 0
  password: ${REDIS_PASSWORD}
  max_connections: 100

database:
  host: localhost
  port: 5432
  name: collaboration
  user: ${DB_USER}
  password: ${DB_PASSWORD}
  pool_size: 20

presence:
  enabled: true
  update_interval_ms: 200
  idle_timeout_seconds: 300
  cleanup_interval_seconds: 60

monitoring:
  metrics_enabled: true
  metrics_port: 9090
  log_level: info
EOF

# Validate configuration
python src/validate_config.py config/collaboration_config.yaml

# Reload configuration (no restart)
curl -X POST http://localhost:8080/api/admin/reload-config

# Or restart to apply changes
sudo systemctl restart collaboration-server
```

#### Manage Connections
```bash
# List active connections
curl -s http://localhost:8080/api/admin/connections | \
  jq '.connections[] | {user_id, document_id, connected_at, ip_address}'

# Check specific user connections
USER_ID="user-123"
curl -s "http://localhost:8080/api/admin/connections?user_id=$USER_ID" | jq .

# Disconnect user (force logout)
curl -X DELETE "http://localhost:8080/api/admin/connections/$USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Broadcast message to all users
curl -X POST http://localhost:8080/api/admin/broadcast \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "type": "announcement",
    "message": "Server maintenance in 10 minutes",
    "priority": "high"
  }'

# Gracefully close all connections
curl -X POST http://localhost:8080/api/admin/graceful-shutdown \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"timeout_seconds": 30}'
```

### Document Operations

#### Create and Manage Documents
```bash
# Create new document
curl -X POST http://localhost:8080/api/documents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "title": "Project Proposal",
    "content": "",
    "permissions": {
      "owner": "user-123",
      "editors": ["user-456", "user-789"],
      "viewers": []
    }
  }'

# Get document
DOC_ID="doc-12345"
curl -s http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $USER_TOKEN" | jq .

# Update document metadata
curl -X PATCH http://localhost:8080/api/documents/$DOC_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"title": "Updated Project Proposal"}'

# Delete document
curl -X DELETE http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $USER_TOKEN"

# List user's documents
curl -s "http://localhost:8080/api/documents?user_id=$USER_ID" \
  -H "Authorization: Bearer $USER_TOKEN" | \
  jq '.documents[] | {id, title, updated_at}'
```

#### Document Collaboration
```bash
# Join document editing session
# (This is typically done via WebSocket from client)

# View active collaborators
curl -s http://localhost:8080/api/documents/$DOC_ID/collaborators \
  -H "Authorization: Bearer $USER_TOKEN" | \
  jq '.collaborators[] | {user_id, name, online, cursor_position}'

# View document operation history
curl -s http://localhost:8080/api/documents/$DOC_ID/operations?limit=100 \
  -H "Authorization: Bearer $USER_TOKEN" | \
  jq '.operations[] | {timestamp, user, operation_type, content}'

# Export document version history
curl -s http://localhost:8080/api/documents/$DOC_ID/versions \
  -H "Authorization: Bearer $USER_TOKEN" | \
  jq . > document_history.json

# Restore document to specific version
VERSION_ID="ver-67890"
curl -X POST http://localhost:8080/api/documents/$DOC_ID/restore \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d "{\"version_id\": \"$VERSION_ID\"}"
```

### Operational Transform Management

#### Monitor OT Engine
```bash
# Check OT engine status
curl -s http://localhost:8080/api/ot/status | \
  jq '{running, queues, transformations_per_second}'

# View transformation metrics
curl -s http://localhost:8080/api/metrics/ot | \
  jq '{
    total_transformations,
    transformation_time_ms_avg,
    conflicts_resolved,
    conflicts_failed
  }'

# Check specific document queue
curl -s "http://localhost:8080/api/ot/queue/$DOC_ID" | \
  jq '{depth, processing_rate, oldest_operation_age_ms}'

# View recent transformations
redis-cli LRANGE "ot:transformations:doc-12345" 0 20
```

#### Test OT Operations
```bash
# Test OT transformation
curl -X POST http://localhost:8080/api/ot/test \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [
      {"type": "insert", "position": 0, "text": "Hello"},
      {"type": "insert", "position": 0, "text": "World"}
    ]
  }'

# Simulate concurrent operations
python src/test_concurrent_operations.py \
  --document-id doc-12345 \
  --users 10 \
  --operations 100

# Check OT correctness
python src/verify_ot_consistency.py --document-id doc-12345
```

#### Clear Operation Queue
```bash
# Clear specific document queue (emergency)
DOC_ID="doc-12345"
curl -X DELETE "http://localhost:8080/api/ot/queue/$DOC_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Or via Redis
redis-cli DEL "operations:queue:$DOC_ID"

# Trigger CRDT reconciliation after clearing
curl -X POST http://localhost:8080/api/crdt/reconcile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"document_id\": \"$DOC_ID\"}"
```

### CRDT Operations

#### Trigger CRDT Sync
```bash
# Manual CRDT sync for document
DOC_ID="doc-12345"
curl -X POST http://localhost:8080/api/crdt/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"document_id\": \"$DOC_ID\"}"

# Sync all documents
curl -X POST http://localhost:8080/api/crdt/sync-all \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Check CRDT sync status
curl -s http://localhost:8080/api/crdt/status | \
  jq '{
    last_sync,
    documents_synced,
    conflicts_resolved,
    errors
  }'
```

#### CRDT Reconciliation
```bash
# Reconcile after conflict
curl -X POST http://localhost:8080/api/crdt/reconcile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "document_id": "doc-12345",
    "strategy": "last_write_wins"
  }'

# Compare OT and CRDT states
curl -s "http://localhost:8080/api/crdt/compare/$DOC_ID" | \
  jq '{ot_state, crdt_state, differences}'

# Force CRDT recovery
curl -X POST http://localhost:8080/api/crdt/recover \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"document_id\": \"$DOC_ID\", \"source\": \"database\"}"
```

### Presence Management

#### View Presence Data
```bash
# Get all active users
curl -s http://localhost:8080/api/presence/users | \
  jq '.users[] | {user_id, document_id, status, last_activity}'

# Get document-specific presence
DOC_ID="doc-12345"
curl -s "http://localhost:8080/api/presence/document/$DOC_ID" | \
  jq '.users[] | {user_id, name, cursor, selection, color}'

# Check user's presence across documents
USER_ID="user-123"
curl -s "http://localhost:8080/api/presence/user/$USER_ID" | jq .

# View awareness states
curl -s http://localhost:8080/api/presence/awareness | \
  jq '.states[] | {user_id, state: .user.state}'
```

#### Manage Presence
```bash
# Update user presence manually
curl -X PUT http://localhost:8080/api/presence \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "document_id": "doc-12345",
    "cursor": {"line": 10, "column": 5},
    "selection": {"start": {"line": 10, "column": 5}, "end": {"line": 10, "column": 15}},
    "status": "active"
  }'

# Clear stale presence data
curl -X POST http://localhost:8080/api/admin/presence/cleanup \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Or via Redis
redis-cli KEYS "presence:*" | xargs redis-cli DEL
```

### Authentication and Authorization

#### Manage JWT Tokens
```bash
# Generate JWT token
python src/generate_jwt.py \
  --user-id user-123 \
  --username "john.doe@example.com" \
  --expiry 3600

# Verify JWT token
TOKEN="eyJhbGciOiJIUzI1NiIs..."
curl -X POST http://localhost:8080/api/auth/verify \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\"}"

# Refresh token
curl -X POST http://localhost:8080/api/auth/refresh \
  -H "Authorization: Bearer $TOKEN"

# Revoke token
curl -X POST http://localhost:8080/api/auth/revoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"token\": \"$TOKEN\"}"

# List revoked tokens
redis-cli SMEMBERS "auth:revoked_tokens"
```

#### Manage Document Permissions
```bash
# Get document permissions
DOC_ID="doc-12345"
curl -s "http://localhost:8080/api/documents/$DOC_ID/permissions" \
  -H "Authorization: Bearer $USER_TOKEN" | jq .

# Add editor
curl -X POST "http://localhost:8080/api/documents/$DOC_ID/permissions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "user_id": "user-456",
    "role": "editor"
  }'

# Remove access
curl -X DELETE "http://localhost:8080/api/documents/$DOC_ID/permissions/user-456" \
  -H "Authorization: Bearer $USER_TOKEN"

# Change ownership
curl -X PUT "http://localhost:8080/api/documents/$DOC_ID/owner" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"new_owner": "user-789"}'
```

### Performance Optimization

#### Scale WebSocket Servers
```bash
# Check current load distribution
for server in collab-{01..04}.example.com; do
  echo "=== $server ==="
  curl -s http://$server:8080/api/metrics/connections | \
    jq '{connections, cpu_usage, memory_usage}'
done

# Add new server to load balancer
# (HAProxy example)
sudo bash -c "cat >> /etc/haproxy/haproxy.cfg << 'EOF'
  server collab-05 collab-05.example.com:8080 check
EOF"
sudo systemctl reload haproxy

# Gracefully drain server for maintenance
SERVER="collab-03.example.com"
curl -X POST http://$SERVER:8080/api/admin/drain \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"timeout_seconds": 300}'

# Wait for connections to drain
watch "curl -s http://$SERVER:8080/api/metrics/connections | jq .total_connections"

# Remove from load balancer when drained
# Update HAProxy config and reload
```

#### Optimize Redis Performance
```bash
# Check Redis memory usage
redis-cli INFO memory

# Check slow queries
redis-cli SLOWLOG GET 10

# Analyze key space
redis-cli --bigkeys

# Enable Redis persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# Optimize connection pool
vim config/collaboration_config.yaml
# redis:
#   max_connections: 200
#   min_idle_connections: 50

sudo systemctl restart collaboration-server
```

#### Tune OT Processing
```bash
# Adjust batch processing
curl -X POST http://localhost:8080/api/admin/ot/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "batch_size": 20,
    "batch_timeout_ms": 30,
    "worker_threads": 8
  }'

# Enable operation compression
vim config/collaboration_config.yaml
# operational_transform:
#   compression_enabled: true
#   compression_threshold_bytes: 1024

sudo systemctl restart collaboration-server
```

---

## Incident Response

### Detection

**Automated Detection:**
- WebSocket connection monitoring
- Operation latency alerts
- Queue depth alerts
- CRDT consistency checks

**Manual Detection:**
```bash
# Check system health
curl http://localhost:8080/health

# Review error logs
tail -100 logs/collaboration-server.log | grep -i error

# Check WebSocket connections
curl -s http://localhost:8080/api/metrics/connections | \
  jq '{connections, errors, drops}'

# Check operation queues
curl -s http://localhost:8080/api/metrics/queues | \
  jq '.queues | map(select(.depth > 100))'

# Check Redis
redis-cli INFO | grep -E "used_memory|connected_clients|rejected_connections"

# Check database connections
psql -h localhost -U collaboration -d collaboration -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

### Triage

#### Severity Classification

**P0: Complete Service Outage**
- WebSocket gateway down
- All operations failing
- Data loss occurring
- Authentication system down

**P1: Degraded Service**
- High operation latency (>200ms)
- Partial WebSocket failures
- CRDT reconciliation failing
- Some users unable to connect

**P2: Performance Issues**
- Elevated latency (100-200ms)
- Slow presence updates
- Queue depths increasing
- Individual connection drops

**P3: Minor Issues**
- Occasional operation retry
- Single document sync issue
- Non-critical logging errors

### Incident Response Procedures

#### P0: WebSocket Gateway Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check gateway status
sudo systemctl status collaboration-server

# 2. Check logs
sudo journalctl -u collaboration-server -n 100 --no-pager

# 3. Attempt restart
sudo systemctl restart collaboration-server

# 4. Verify restart
curl -f http://localhost:8080/health

# 5. If restart fails, start manually for debugging
cd /home/user/Portfolio-Project/projects/15-real-time-collaboration
source venv/bin/activate
python src/collaboration_server.py --debug 2>&1 | tee /tmp/collab-debug.log
```

**Investigation (5-20 minutes):**
```bash
# Check dependencies
systemctl status redis
systemctl status postgresql

# Test Redis connectivity
redis-cli ping

# Test database connectivity
psql -h localhost -U collaboration -d collaboration -c "SELECT 1;"

# Check system resources
free -h
df -h
ps aux | grep collaboration_server

# Check for port conflicts
sudo netstat -tlnp | grep 8080

# Check firewall
sudo iptables -L -n | grep 8080

# Review recent changes
git log -10 --oneline
```

**Recovery:**
```bash
# If dependency issue, restart dependencies
sudo systemctl restart redis postgresql
sleep 10
sudo systemctl restart collaboration-server

# If port conflict, change port
vim config/collaboration_config.yaml
# server:
#   port: 8081
sudo systemctl restart collaboration-server

# If configuration error
cp config/collaboration_config.yaml.backup config/collaboration_config.yaml
sudo systemctl restart collaboration-server

# If persistent issues, failover to backup server
# Update load balancer to redirect traffic
sudo haproxy-update --disable collab-01 --enable collab-02

# Verify recovery
curl http://localhost:8080/health
curl -s http://localhost:8080/api/metrics/connections | jq .
```

#### P0: All Operations Failing

**Immediate Actions (0-10 minutes):**
```bash
# 1. Check OT engine status
curl -s http://localhost:8080/api/ot/status

# 2. Check Redis (operation queue storage)
redis-cli ping
redis-cli INFO | grep used_memory

# 3. Check operation queue
redis-cli KEYS "operations:queue:*" | head -20

# 4. Test simple operation
curl -X POST http://localhost:8080/api/documents/test-doc/operations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "operations": [{"type": "insert", "position": 0, "text": "test"}]
  }'

# 5. Check error logs
tail -100 logs/ot-engine.log | grep -i error
```

**Investigation:**
```bash
# Check Redis memory
redis-cli INFO memory | grep used_memory_human

# Check if Redis is full
redis-cli CONFIG GET maxmemory

# Check database operations
psql -h localhost -U collaboration -d collaboration << 'EOF'
SELECT COUNT(*) FROM operations WHERE created_at > NOW() - INTERVAL '1 hour';
SELECT COUNT(*) FROM pg_stat_activity;
EOF

# Check OT transformation errors
curl -s http://localhost:8080/api/metrics/ot | \
  jq '{conflicts_failed, transformation_errors}'

# Test OT logic
python src/test_ot_correctness.py --verbose
```

**Recovery:**
```bash
# If Redis memory full
redis-cli CONFIG SET maxmemory 4gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Clean old data
redis-cli KEYS "operations:processed:*" | xargs redis-cli DEL

# If OT engine issue, restart workers
curl -X POST http://localhost:8080/api/admin/ot/restart \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# If database deadlock
psql -h localhost -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='collaboration' AND state='idle in transaction';"

# Enable CRDT fallback
curl -X POST http://localhost:8080/api/admin/enable-crdt-fallback \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify recovery
curl -X POST http://localhost:8080/api/documents/test-doc/operations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"operations": [{"type": "insert", "position": 0, "text": "recovery test"}]}'
```

#### P1: High Operation Latency

**Investigation:**
```bash
# Check current latency
curl -s http://localhost:8080/api/metrics | \
  jq '{operation_latency_p50, operation_latency_p95, operation_latency_p99}'

# Check queue depths
curl -s http://localhost:8080/api/metrics/queues | \
  jq '.queues | map(select(.depth > 50)) | length'

# Check Redis latency
redis-cli --latency

# Check database query performance
psql -h localhost -U collaboration -d collaboration -c \
  "SELECT query, calls, mean_time, max_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;"

# Check system load
uptime
iostat -x 1 5
```

**Mitigation:**
```bash
# Increase OT workers
curl -X POST http://localhost:8080/api/admin/ot/scale \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"workers": 8}'

# Increase batch size to reduce overhead
curl -X POST http://localhost:8080/api/admin/ot/config \
  -d '{"batch_size": 50, "batch_timeout_ms": 100}'

# Enable operation compression
curl -X POST http://localhost:8080/api/admin/compression/enable

# Scale Redis if needed
# Add Redis replicas for read scaling

# Optimize database queries
psql -h localhost -U collaboration -d collaboration << 'EOF'
CREATE INDEX IF NOT EXISTS idx_operations_document_created
  ON operations (document_id, created_at DESC);
VACUUM ANALYZE operations;
EOF

# Monitor improvement
watch -n 2 'curl -s http://localhost:8080/api/metrics | jq .operation_latency_p95'
```

#### P1: CRDT Reconciliation Failures

**Investigation:**
```bash
# Check CRDT sync status
curl -s http://localhost:8080/api/crdt/status | \
  jq '{last_sync, errors, failed_documents}'

# List failed reconciliations
curl -s "http://localhost:8080/api/crdt/failures?since=1h" | \
  jq '.failures[] | {document_id, error, timestamp}'

# Compare OT and CRDT states
DOC_ID="doc-12345"
curl -s "http://localhost:8080/api/crdt/compare/$DOC_ID" | \
  jq '{differences, ot_operations_count, crdt_version}'

# Check CRDT logs
grep "CRDT" logs/collaboration-server.log | tail -50
```

**Recovery:**
```bash
# Force CRDT sync for specific document
curl -X POST http://localhost:8080/api/crdt/force-sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "document_id": "doc-12345",
    "source": "ot_state"
  }'

# If OT state is corrupted, recover from database
curl -X POST http://localhost:8080/api/crdt/recover \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "document_id": "doc-12345",
    "source": "database",
    "rebuild_ot_queue": true
  }'

# If CRDT state is corrupted, rebuild from operations
python src/rebuild_crdt_state.py \
  --document-id doc-12345 \
  --from-operations

# Verify state consistency
python src/verify_document_consistency.py \
  --document-id doc-12345 \
  --check-all-states
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/collab-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Collaboration Platform Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 45 minutes
**Affected Documents:** 15 documents, 120 users

## Timeline
- 14:00: Alert - high operation latency detected
- 14:05: Identified Redis memory exhaustion
- 14:10: Increased Redis maxmemory limit
- 14:15: Cleared old operation cache
- 14:30: Latency returned to normal
- 14:45: Incident closed

## Root Cause
Redis maxmemory limit too low for operation queue cache growth

## Actions Taken
- Increased Redis maxmemory to 4GB
- Implemented LRU eviction policy
- Cleared old cached operations
- Enabled compression for operations

## Action Items
- [ ] Implement Redis memory monitoring
- [ ] Add automatic cache cleanup
- [ ] Review operation retention policy
- [ ] Scale Redis cluster

EOF

# Update monitoring
# Add Redis memory alert
cat >> config/alerts.yaml << 'EOF'
- name: RedisMemoryHigh
  condition: redis_used_memory_bytes / redis_maxmemory_bytes > 0.85
  for: 5m
  severity: warning
  action: alert-ops-team
EOF

# Test improvements
python src/load_test.py \
  --users 1000 \
  --documents 100 \
  --operations 10000 \
  --report load_test_$(date +%Y%m%d).html
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 5 minutes (operation log retention)
- **RTO** (Recovery Time Objective): 10 minutes (failover to standby)

### Backup Strategy

**Document Backup:**
```bash
# Backup documents database
pg_dump -h localhost -U collaboration collaboration | \
  gzip > backups/collaboration_db_$(date +%Y%m%d-%H%M).sql.gz

# Upload to S3
aws s3 cp backups/collaboration_db_$(date +%Y%m%d-%H%M).sql.gz \
  s3://collab-backups/database/

# Automated backup script
cat > /etc/cron.hourly/collab-backup << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M)
pg_dump -h localhost -U collaboration collaboration | gzip > /backups/collab_$TIMESTAMP.sql.gz
aws s3 cp /backups/collab_$TIMESTAMP.sql.gz s3://collab-backups/database/
find /backups -name "collab_*.sql.gz" -mtime +7 -delete
EOF
chmod +x /etc/cron.hourly/collab-backup
```

**Redis Backup:**
```bash
# Snapshot Redis data
redis-cli BGSAVE

# Wait for save to complete
while [ $(redis-cli LASTSAVE) -eq $LAST_SAVE ]; do sleep 1; done

# Copy snapshot
cp /var/lib/redis/dump.rdb backups/redis_$(date +%Y%m%d-%H%M).rdb
aws s3 cp backups/redis_$(date +%Y%m%d-%H%M).rdb s3://collab-backups/redis/
```

### Disaster Recovery Procedures

#### Complete System Loss

**Recovery Steps (10-20 minutes):**
```bash
# 1. Provision new infrastructure
terraform apply -auto-approve

# 2. Restore database
aws s3 cp s3://collab-backups/database/latest.sql.gz .
gunzip < latest.sql.gz | psql -h localhost -U collaboration collaboration

# 3. Restore Redis
aws s3 cp s3://collab-backups/redis/latest.rdb /var/lib/redis/dump.rdb
systemctl restart redis

# 4. Deploy application
git pull origin main
pip install -r requirements.txt
sudo systemctl start collaboration-server

# 5. Verify system
curl http://localhost:8080/health
curl -s http://localhost:8080/api/documents | jq '.documents | length'

# 6. Resume client connections
# Update DNS to point to new servers
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Morning health check
./scripts/daily_health_check.sh

# Review connection metrics
curl -s http://localhost:8080/api/metrics/connections | jq .

# Check operation queue depths
curl -s http://localhost:8080/api/metrics/queues | jq '.queues | map(.depth) | max'

# Review error logs
grep -i error logs/collaboration-server.log | tail -20
```

### Weekly Tasks
```bash
# Clean old operations from Redis
redis-cli EVAL "return redis.call('DEL', unpack(redis.call('KEYS', 'operations:processed:*')))" 0

# Vacuum database
psql -h localhost -U collaboration -d collaboration -c "VACUUM ANALYZE;"

# Review performance trends
python src/generate_performance_report.py --period 7days --output reports/weekly_$(date +%Y%m%d).html

# Update dependencies
pip list --outdated
```

### Monthly Tasks
```bash
# Review and archive old documents
python src/archive_inactive_documents.py --inactive-days 90

# Security audit
./scripts/security_audit.sh

# Load testing
python src/load_test.py --users 5000 --duration 1h

# Update servers
sudo apt-get update && sudo apt-get upgrade -y
sudo systemctl restart collaboration-server
```

---

## Quick Reference

### Most Common Operations
```bash
# Check server status
curl http://localhost:8080/health

# View active connections
curl -s http://localhost:8080/api/metrics/connections | jq .

# Check operation latency
curl -s http://localhost:8080/api/metrics | jq .operation_latency_p95

# View document activity
curl -s "http://localhost:8080/api/documents/active" | jq .

# Force CRDT sync
curl -X POST http://localhost:8080/api/crdt/sync-all

# Restart server
sudo systemctl restart collaboration-server
```

### Emergency Response
```bash
# P0: Gateway down
sudo systemctl restart collaboration-server
curl http://localhost:8080/health

# P0: Operations failing
redis-cli CONFIG SET maxmemory 4gb
curl -X POST http://localhost:8080/api/admin/ot/restart

# P1: High latency
curl -X POST http://localhost:8080/api/admin/ot/scale -d '{"workers": 8}'

# P1: CRDT failures
curl -X POST http://localhost:8080/api/crdt/force-sync -d '{"document_id": "doc-12345"}'
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Collaboration Platform Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
