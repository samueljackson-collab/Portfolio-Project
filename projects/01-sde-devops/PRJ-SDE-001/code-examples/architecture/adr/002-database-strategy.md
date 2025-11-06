# ADR 002: Polyglot Persistence with Database Per Service

## Status
Accepted

## Context
With microservices architecture, we need to determine database strategy that balances data consistency, service independence, and operational complexity.

### Requirements
- Service data independence
- Transactional integrity where needed
- High read performance for product catalog
- Real-time analytics capabilities
- Cost-effective at scale

### Options Considered

#### Option 1: Shared Database
**Pros:**
- ACID transactions across services
- Simpler data consistency
- Single backup/recovery process
- Lower infrastructure cost

**Cons:**
- Tight coupling between services
- Schema changes affect multiple services
- Scaling bottleneck
- Team dependencies

#### Option 2: Database Per Service (Chosen)
**Pros:**
- Service independence
- Technology choice per service
- Easier to scale
- Clearer ownership

**Cons:**
- Distributed transactions complexity
- Data duplication
- More databases to manage
- Eventual consistency

## Decision
Adopt **Database Per Service** with polyglot persistence:

### Service Database Mapping

| Service | Database | Rationale |
|---------|----------|-----------|
| User Service | PostgreSQL | ACID, complex queries, mature |
| Product Service | PostgreSQL | Inventory consistency needed |
| Order Service | PostgreSQL | Transactional integrity critical |
| Payment Service | PostgreSQL | Financial data, ACID required |
| Search Service | Elasticsearch | Full-text search, faceted search |
| Analytics Service | ClickHouse | Time-series data, fast aggregations |
| Session Service | Redis | Fast access, TTL support |
| Cache Layer | Redis | Low latency, high throughput |

### Data Consistency Strategy

#### Strong Consistency (Within Service)
- Use PostgreSQL transactions
- ACID guarantees within service boundary

#### Eventual Consistency (Cross-Service)
- Event-driven architecture
- Saga pattern for distributed transactions
- Event sourcing for critical workflows

#### Implementation Pattern

```typescript
// Saga Pattern Example: Order Creation
class OrderSaga {
  async createOrder(orderData) {
    const sagaId = generateId();

    try {
      // Step 1: Reserve inventory
      const inventoryReserved = await this.reserveInventory(
        orderData.items,
        sagaId
      );

      // Step 2: Process payment
      const paymentProcessed = await this.processPayment(
        orderData.payment,
        sagaId
      );

      // Step 3: Create order
      const order = await this.createOrderRecord(
        orderData,
        sagaId
      );

      // Step 4: Send notification
      await this.sendOrderConfirmation(order.id);

      return order;

    } catch (error) {
      // Compensating transactions
      await this.compensate(sagaId, error);
      throw error;
    }
  }

  async compensate(sagaId, error) {
    await this.releaseInventory(sagaId);
    await this.refundPayment(sagaId);
    await this.markOrderFailed(sagaId, error);
  }
}
```

### Data Replication Strategy

#### Read Replicas
- Each PostgreSQL database has 1-2 read replicas
- Read-heavy queries directed to replicas
- Automatic failover configured

#### Cache Strategy
```typescript
// Multi-level caching
class DataAccessLayer {
  async getProduct(id: string) {
    // L1: Application cache (in-memory)
    let product = this.memoryCache.get(id);
    if (product) return product;

    // L2: Redis cache
    product = await this.redis.get(`product:${id}`);
    if (product) {
      this.memoryCache.set(id, product);
      return product;
    }

    // L3: Database
    product = await this.db.products.findById(id);
    if (product) {
      await this.redis.setex(`product:${id}`, 3600, product);
      this.memoryCache.set(id, product);
    }

    return product;
  }
}
```

### Backup Strategy
- Daily automated backups for all databases
- Point-in-time recovery (PITR) enabled
- Cross-region backup replication
- 30-day retention for production
- 7-day retention for staging

### Monitoring
- Query performance monitoring
- Slow query logging
- Connection pool monitoring
- Replication lag monitoring
- Disk space alerts

## Consequences

### Positive
- Services can evolve independently
- Right tool for each use case
- Better performance optimization
- Clearer data ownership

### Negative
- More databases to manage
- Eventual consistency complexity
- Data duplication
- Higher infrastructure cost
- Requires skilled operations team

### Mitigation
- Automated database provisioning (Terraform)
- Centralized monitoring (Datadog/NewRelic)
- Database reliability engineering team
- Comprehensive documentation
- Standardized backup procedures

## Implementation Timeline
- Month 1: PostgreSQL for core services
- Month 2: Redis caching layer
- Month 3: Elasticsearch for search
- Month 4: ClickHouse for analytics

## Review
Review this decision in 6 months based on:
- Operational complexity
- Performance metrics
- Team productivity
- Infrastructure costs
