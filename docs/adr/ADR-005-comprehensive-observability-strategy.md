# ADR-005: Comprehensive Observability Strategy

> **Historical snapshot**: This ADR captures the 2024 observability strategy decision record. For current monitoring operations, see the [Observability Runbook](../runbooks/observability-runbook.md).

## Status
Accepted - December 2024

## Context
Need complete visibility into distributed system with 15+ microservices. Current monitoring inadequate for troubleshooting production issues.

## Requirements
- End-to-end request tracing
- Real-time metrics and alerting
- Log aggregation and search
- Service dependency mapping
- SLA/SLO tracking
- Root cause analysis capabilities

## Decision
Implement **Three Pillars of Observability**:
1. **Metrics**: Prometheus + Grafana
2. **Logs**: Loki + Grafana
3. **Traces**: Tempo + Grafana

## Architecture Overview

```yaml
# Observability Stack
┌─────────────────────────────────────────────────────────┐
│                    Applications                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Service A│ │ Service B│ │ Service C│ │ Service D│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │          │
└───────┼────────────┼────────────┼────────────┼──────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────┐
│                  Collection Layer                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │Prometheus│ │  Loki    │ │  Tempo   │               │
│  │ Metrics  │ │  Logs    │ │  Traces  │               │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘               │
└───────┼────────────┼────────────┼─────────────────────┘
        │            │            │
        └────────────┴────────────┘
                     │
                     ▼
            ┌────────────────┐
            │    Grafana     │
            │  Dashboards    │
            └────────────────┘
```

## 1. Metrics Implementation (Prometheus)

```typescript
// metrics.ts - Application metrics
import { Registry, Counter, Histogram, Gauge } from 'prom-client';

export class MetricsService {
  private registry: Registry;

  // HTTP Metrics
  private httpRequestDuration: Histogram;
  private httpRequestTotal: Counter;
  private httpRequestErrors: Counter;

  // Business Metrics
  private ordersCreated: Counter;
  private orderValue: Histogram;
  private activeUsers: Gauge;

  // System Metrics
  private databaseConnections: Gauge;
  private cacheHitRate: Gauge;
  private queueSize: Gauge;

  constructor() {
    this.registry = new Registry();

    // HTTP metrics
    this.httpRequestDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status'],
      buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]
    });

    this.httpRequestTotal = new Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status']
    });

    this.httpRequestErrors = new Counter({
      name: 'http_request_errors_total',
      help: 'Total number of HTTP request errors',
      labelNames: ['method', 'route', 'error_type']
    });

    // Business metrics
    this.ordersCreated = new Counter({
      name: 'orders_created_total',
      help: 'Total number of orders created',
      labelNames: ['status', 'payment_method']
    });

    this.orderValue = new Histogram({
      name: 'order_value_dollars',
      help: 'Value of orders in dollars',
      buckets: [10, 50, 100, 500, 1000, 5000]
    });

    this.activeUsers = new Gauge({
      name: 'active_users',
      help: 'Number of active users'
    });

    // System metrics
    this.databaseConnections = new Gauge({
      name: 'database_connections_active',
      help: 'Number of active database connections',
      labelNames: ['pool', 'database']
    });

    this.cacheHitRate = new Gauge({
      name: 'cache_hit_rate',
      help: 'Cache hit rate percentage',
      labelNames: ['cache_layer']
    });

    this.queueSize = new Gauge({
      name: 'queue_size',
      help: 'Number of messages in queue',
      labelNames: ['queue_name']
    });

    // Register all metrics
    this.registry.registerMetric(this.httpRequestDuration);
    this.registry.registerMetric(this.httpRequestTotal);
    this.registry.registerMetric(this.httpRequestErrors);
    this.registry.registerMetric(this.ordersCreated);
    this.registry.registerMetric(this.orderValue);
    this.registry.registerMetric(this.activeUsers);
    this.registry.registerMetric(this.databaseConnections);
    this.registry.registerMetric(this.cacheHitRate);
    this.registry.registerMetric(this.queueSize);
  }

  // Track HTTP request
  recordHttpRequest(method: string, route: string, status: number, duration: number) {
    this.httpRequestDuration.observe({ method, route, status }, duration);
    this.httpRequestTotal.inc({ method, route, status });
  }

  // Track business events
  recordOrderCreated(status: string, paymentMethod: string, value: number) {
    this.ordersCreated.inc({ status, payment_method: paymentMethod });
    this.orderValue.observe(value);
  }

  // Update system metrics
  updateDatabaseConnections(pool: string, database: string, count: number) {
    this.databaseConnections.set({ pool, database }, count);
  }

  // Expose metrics endpoint
  async getMetrics(): Promise<string> {
    return this.registry.metrics();
  }
}

// Express middleware
export function metricsMiddleware(metrics: MetricsService) {
  return (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();

    res.on('finish', () => {
      const duration = (Date.now() - start) / 1000;
      metrics.recordHttpRequest(
        req.method,
        req.route?.path || req.path,
        res.statusCode,
        duration
      );
    });

    next();
  };
}
```

## 2. Distributed Tracing (Tempo)

```typescript
// tracing.ts - OpenTelemetry setup
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

export function initializeTracing(serviceName: string) {
  const sdk = new NodeSDK({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
      [SemanticResourceAttributes.SERVICE_VERSION]: process.env.APP_VERSION || '1.0.0',
      [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development'
    }),
    traceExporter: new OTLPTraceExporter({
      url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://tempo:4318/v1/traces',
    }),
    instrumentations: [
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-http': {
          requestHook: (span, request) => {
            span.setAttribute('http.user_agent', request.headers['user-agent']);
            span.setAttribute('http.client_ip', request.headers['x-forwarded-for'] || request.socket.remoteAddress);
          }
        },
        '@opentelemetry/instrumentation-express': {
          enabled: true
        },
        '@opentelemetry/instrumentation-pg': {
          enabled: true
        },
        '@opentelemetry/instrumentation-redis': {
          enabled: true
        }
      })
    ]
  });

  sdk.start();

  // Graceful shutdown
  process.on('SIGTERM', () => {
    sdk.shutdown()
      .then(() => console.log('Tracing terminated'))
      .catch((error) => console.error('Error terminating tracing', error))
      .finally(() => process.exit(0));
  });

  return sdk;
}

// Custom span creation
import { trace, SpanStatusCode } from '@opentelemetry/api';

export class TracingService {
  private tracer = trace.getTracer('portfolio-service');

  async traceOperation<T>(
    operationName: string,
    attributes: Record<string, string | number>,
    operation: () => Promise<T>
  ): Promise<T> {
    const span = this.tracer.startSpan(operationName, {
      attributes
    });

    try {
      const result = await operation();
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error instanceof Error ? error.message : 'Unknown error'
      });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  }
}

// Usage in service
class OrderService {
  private tracing = new TracingService();

  async createOrder(orderData: CreateOrderDTO): Promise<Order> {
    return this.tracing.traceOperation(
      'createOrder',
      {
        'order.user_id': orderData.userId,
        'order.item_count': orderData.items.length,
        'order.total_value': orderData.totalValue
      },
      async () => {
        // Your business logic here
        const order = await this.db.orders.create(orderData);
        return order;
      }
    );
  }
}
```

## 3. Structured Logging (Loki)

```typescript
// logger.ts - Structured logging
import winston from 'winston';
import LokiTransport from 'winston-loki';

export function createLogger(serviceName: string) {
  const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    ),
    defaultMeta: {
      service: serviceName,
      environment: process.env.NODE_ENV,
      version: process.env.APP_VERSION
    },
    transports: [
      // Console for development
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.simple()
        )
      }),
      // Loki for production
      new LokiTransport({
        host: process.env.LOKI_HOST || 'http://loki:3100',
        labels: {
          service: serviceName,
          environment: process.env.NODE_ENV || 'development'
        },
        json: true,
        format: winston.format.json(),
        replaceTimestamp: true,
        onConnectionError: (err) => console.error('Loki connection error:', err)
      })
    ]
  });

  return logger;
}

// Usage with context
class OrderService {
  private logger = createLogger('order-service');

  async createOrder(orderData: CreateOrderDTO, userId: string): Promise<Order> {
    const correlationId = generateCorrelationId();

    this.logger.info('Creating order', {
      correlationId,
      userId,
      itemCount: orderData.items.length,
      totalValue: orderData.totalValue
    });

    try {
      const order = await this.db.orders.create(orderData);

      this.logger.info('Order created successfully', {
        correlationId,
        orderId: order.id,
        userId,
        duration: Date.now() - startTime
      });

      return order;
    } catch (error) {
      this.logger.error('Order creation failed', {
        correlationId,
        userId,
        error: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });

      throw error;
    }
  }
}
```

## 4. Alerting Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_request_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for {{ $labels.service }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s for {{ $labels.service }}"

      - alert: DatabaseConnectionPoolExhaustion
        expr: |
          database_connections_active / database_connections_max > 0.9
        for: 5m
        labels:
          severity: critical
          team: database
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool at {{ $value | humanizePercentage }} capacity"

      - alert: CacheLowHitRate
        expr: |
          cache_hit_rate < 0.7
        for: 15m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Cache hit rate below threshold"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"

  - name: business_alerts
    interval: 1m
    rules:
      - alert: OrderCreationRateDropped
        expr: |
          rate(orders_created_total[10m]) < 0.5 * rate(orders_created_total[1h] offset 1h)
        for: 10m
        labels:
          severity: critical
          team: business
        annotations:
          summary: "Order creation rate dropped significantly"
          description: "Current rate is 50% below normal"

      - alert: HighOrderFailureRate
        expr: |
          rate(orders_created_total{status="failed"}[5m]) / rate(orders_created_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
          team: business
        annotations:
          summary: "High order failure rate"
          description: "{{ $value | humanizePercentage }} of orders are failing"
```

## 5. Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Application Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum(rate(http_request_errors_total[5m])) by (service, error_type)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "active_users"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

## SLI/SLO Tracking

```yaml
# Service Level Objectives
slos:
  - name: api_availability
    description: "API should be available 99.9% of the time"
    target: 0.999
    window: 30d
    sli:
      expr: |
        sum(rate(http_requests_total{status!~"5.."}[30d])) /
        sum(rate(http_requests_total[30d]))

  - name: api_latency
    description: "95% of requests should complete within 500ms"
    target: 0.95
    window: 30d
    sli:
      expr: |
        histogram_quantile(0.95,
          sum(rate(http_request_duration_seconds_bucket[30d])) by (le)
        ) < 0.5

  - name: order_success_rate
    description: "99% of orders should complete successfully"
    target: 0.99
    window: 7d
    sli:
      expr: |
        sum(rate(orders_created_total{status="success"}[7d])) /
        sum(rate(orders_created_total[7d]))
```

## Consequences

### Positive
- Complete visibility into system behavior
- Faster incident resolution (MTTR reduced by 70%)
- Proactive issue detection
- Better capacity planning
- Improved developer productivity

### Negative
- Additional infrastructure costs (~$2,000/month)
- Storage requirements (1TB/month for traces/logs)
- Learning curve for team
- Maintenance overhead

## Success Metrics
- MTTR: 45min → 15min (67% improvement)
- MTTD: 20min → 5min (75% improvement)
- Incident rate: 12/month → 3/month (75% reduction)
- Debug time: 2hrs → 30min (75% reduction)

## Related ADRs
- ADR-004: Multi-Layer Caching Strategy
- ADR-006: Zero-Trust Security Architecture
- ADR-008: Deployment Strategy (planned)

## References
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Grafana Observability](https://grafana.com/docs/)
