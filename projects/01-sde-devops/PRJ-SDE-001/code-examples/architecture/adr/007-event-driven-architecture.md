# ADR 007: Event-Driven Architecture

## Status
Accepted - December 2024

## Context
Microservices need to communicate asynchronously to maintain loose coupling and handle high-volume operations without blocking.

### Requirements
- Asynchronous communication between services
- Event sourcing for critical workflows
- Reliable message delivery
- Event replay capabilities
- Scalability for high-throughput events

## Decision
Implement **Event-Driven Architecture** using:
- AWS SNS/SQS for message queuing
- EventBridge for event routing
- Event sourcing for critical workflows

### Event Schema

```typescript
// events/base.event.ts
export interface BaseEvent {
  id: string;
  type: string;
  timestamp: string;
  version: string;
  source: string;
  correlationId: string;
  causationId?: string;
  userId?: string;
  metadata: Record<string, any>;
}

// events/order.events.ts
export interface OrderCreatedEvent extends BaseEvent {
  type: 'order.created';
  data: {
    orderId: string;
    userId: string;
    items: OrderItem[];
    totalAmount: number;
    currency: string;
    shippingAddress: Address;
    paymentMethod: string;
  };
}

export interface OrderPaidEvent extends BaseEvent {
  type: 'order.paid';
  data: {
    orderId: string;
    paymentId: string;
    amount: number;
    currency: string;
    paymentMethod: string;
  };
}

export interface OrderShippedEvent extends BaseEvent {
  type: 'order.shipped';
  data: {
    orderId: string;
    trackingNumber: string;
    carrier: string;
    estimatedDelivery: string;
  };
}

export interface InventoryReservedEvent extends BaseEvent {
  type: 'inventory.reserved';
  data: {
    orderId: string;
    items: Array<{
      productId: string;
      quantity: number;
      reservationId: string;
    }>;
  };
}
```

### Event Bus Implementation

```typescript
// event-bus.service.ts
import {
  SNSClient,
  PublishCommand
} from '@aws-sdk/client-sns';
import {
  SQSClient,
  SendMessageCommand,
  ReceiveMessageCommand,
  DeleteMessageCommand
} from '@aws-sdk/client-sqs';

export class EventBus {
  private snsClient: SNSClient;
  private sqsClient: SQSClient;
  private topicArn: string;

  constructor() {
    this.snsClient = new SNSClient({ region: process.env.AWS_REGION });
    this.sqsClient = new SQSClient({ region: process.env.AWS_REGION });
    this.topicArn = process.env.SNS_TOPIC_ARN!;
  }

  async publish<T extends BaseEvent>(event: T): Promise<void> {
    const command = new PublishCommand({
      TopicArn: this.topicArn,
      Message: JSON.stringify(event),
      MessageAttributes: {
        eventType: {
          DataType: 'String',
          StringValue: event.type
        },
        correlationId: {
          DataType: 'String',
          StringValue: event.correlationId
        }
      }
    });

    await this.snsClient.send(command);

    logger.info('Event published', {
      eventId: event.id,
      eventType: event.type,
      correlationId: event.correlationId
    });
  }

  async subscribe<T extends BaseEvent>(
    queueUrl: string,
    handler: (event: T) => Promise<void>
  ): Promise<void> {
    while (true) {
      try {
        const command = new ReceiveMessageCommand({
          QueueUrl: queueUrl,
          MaxNumberOfMessages: 10,
          WaitTimeSeconds: 20,
          MessageAttributeNames: ['All']
        });

        const response = await this.sqsClient.send(command);

        if (response.Messages) {
          await Promise.all(
            response.Messages.map(async (message) => {
              try {
                const event = JSON.parse(message.Body!) as T;
                await handler(event);

                // Delete message after successful processing
                await this.sqsClient.send(
                  new DeleteMessageCommand({
                    QueueUrl: queueUrl,
                    ReceiptHandle: message.ReceiptHandle!
                  })
                );
              } catch (error) {
                logger.error('Event processing failed', {
                  messageId: message.MessageId,
                  error
                });
                // Message will be retried or sent to DLQ
              }
            })
          );
        }
      } catch (error) {
        logger.error('Error receiving messages', { error });
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }
}

// Usage in service
class OrderService {
  private eventBus: EventBus;

  async createOrder(orderData: CreateOrderDTO): Promise<Order> {
    const order = await this.repository.create(orderData);

    // Publish event
    await this.eventBus.publish<OrderCreatedEvent>({
      id: generateId(),
      type: 'order.created',
      timestamp: new Date().toISOString(),
      version: '1.0',
      source: 'order-service',
      correlationId: orderData.correlationId,
      userId: orderData.userId,
      metadata: {},
      data: {
        orderId: order.id,
        userId: order.userId,
        items: order.items,
        totalAmount: order.totalAmount,
        currency: order.currency,
        shippingAddress: order.shippingAddress,
        paymentMethod: order.paymentMethod
      }
    });

    return order;
  }
}

// Event handlers
class InventoryService {
  private eventBus: EventBus;

  async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
    logger.info('Reserving inventory', {
      orderId: event.data.orderId,
      items: event.data.items
    });

    const reservations = [];
    for (const item of event.data.items) {
      const reservationId = await this.reserveInventory(
        item.productId,
        item.quantity
      );
      reservations.push({
        productId: item.productId,
        quantity: item.quantity,
        reservationId
      });
    }

    await this.eventBus.publish<InventoryReservedEvent>({
      id: generateId(),
      type: 'inventory.reserved',
      timestamp: new Date().toISOString(),
      version: '1.0',
      source: 'inventory-service',
      correlationId: event.correlationId,
      causationId: event.id,
      metadata: {},
      data: {
        orderId: event.data.orderId,
        items: reservations
      }
    });
  }
}
```

### Event Sourcing

```typescript
// event-store.service.ts
export class EventStore {
  private db: Database;

  async append(event: BaseEvent, aggregateId: string): Promise<void> {
    await this.db.events.create({
      eventId: event.id,
      aggregateId,
      eventType: event.type,
      eventData: event.data,
      timestamp: event.timestamp,
      version: event.version,
      correlationId: event.correlationId,
      causationId: event.causationId,
      metadata: event.metadata
    });
  }

  async getEvents(aggregateId: string): Promise<BaseEvent[]> {
    const events = await this.db.events.find({
      aggregateId,
      orderBy: { timestamp: 'asc' }
    });

    return events.map(e => ({
      id: e.eventId,
      type: e.eventType,
      timestamp: e.timestamp,
      version: e.version,
      source: e.source,
      correlationId: e.correlationId,
      causationId: e.causationId,
      metadata: e.metadata,
      data: e.eventData
    }));
  }

  async replay(aggregateId: string): Promise<any> {
    const events = await this.getEvents(aggregateId);
    let state = {};

    for (const event of events) {
      state = this.applyEvent(state, event);
    }

    return state;
  }

  private applyEvent(state: any, event: BaseEvent): any {
    switch (event.type) {
      case 'order.created':
        return { ...state, ...event.data, status: 'created' };
      case 'order.paid':
        return { ...state, paymentId: event.data.paymentId, status: 'paid' };
      case 'order.shipped':
        return { ...state, trackingNumber: event.data.trackingNumber, status: 'shipped' };
      default:
        return state;
    }
  }
}

// Aggregate using event sourcing
class OrderAggregate {
  private eventStore: EventStore;
  private eventBus: EventBus;
  private state: any;

  constructor(private orderId: string) {
    this.state = {};
  }

  async load(): Promise<void> {
    this.state = await this.eventStore.replay(this.orderId);
  }

  async createOrder(orderData: CreateOrderDTO): Promise<void> {
    const event: OrderCreatedEvent = {
      id: generateId(),
      type: 'order.created',
      timestamp: new Date().toISOString(),
      version: '1.0',
      source: 'order-service',
      correlationId: generateId(),
      metadata: {},
      data: orderData
    };

    // Apply event to local state
    this.state = this.applyEvent(this.state, event);

    // Persist event
    await this.eventStore.append(event, this.orderId);

    // Publish event
    await this.eventBus.publish(event);
  }

  private applyEvent(state: any, event: BaseEvent): any {
    // Same logic as EventStore.applyEvent
    return state;
  }
}
```

### Saga Pattern for Distributed Transactions

```typescript
// saga.service.ts
export class OrderSaga {
  private eventBus: EventBus;
  private sagaRepository: SagaRepository;

  async createOrder(orderData: CreateOrderDTO): Promise<void> {
    const sagaId = generateId();

    // Create saga instance
    const saga = await this.sagaRepository.create({
      sagaId,
      type: 'order-creation',
      status: 'started',
      steps: []
    });

    try {
      // Step 1: Reserve inventory
      await this.executeStep(sagaId, 'reserve-inventory', async () => {
        await this.eventBus.publish({
          id: generateId(),
          type: 'inventory.reserve-requested',
          timestamp: new Date().toISOString(),
          version: '1.0',
          source: 'order-saga',
          correlationId: sagaId,
          metadata: {},
          data: {
            items: orderData.items
          }
        });
      });

      // Step 2: Process payment
      await this.executeStep(sagaId, 'process-payment', async () => {
        await this.eventBus.publish({
          id: generateId(),
          type: 'payment.process-requested',
          timestamp: new Date().toISOString(),
          version: '1.0',
          source: 'order-saga',
          correlationId: sagaId,
          metadata: {},
          data: {
            amount: orderData.totalAmount,
            currency: orderData.currency,
            paymentMethod: orderData.paymentMethod
          }
        });
      });

      // Step 3: Create order
      await this.executeStep(sagaId, 'create-order', async () => {
        await this.eventBus.publish({
          id: generateId(),
          type: 'order.create-requested',
          timestamp: new Date().toISOString(),
          version: '1.0',
          source: 'order-saga',
          correlationId: sagaId,
          metadata: {},
          data: orderData
        });
      });

      // Mark saga as completed
      await this.sagaRepository.update(sagaId, {
        status: 'completed',
        completedAt: new Date()
      });

    } catch (error) {
      // Compensate - undo all completed steps
      await this.compensate(sagaId);
      throw error;
    }
  }

  private async executeStep(
    sagaId: string,
    stepName: string,
    action: () => Promise<void>
  ): Promise<void> {
    await this.sagaRepository.addStep(sagaId, {
      name: stepName,
      status: 'started',
      startedAt: new Date()
    });

    try {
      await action();

      await this.sagaRepository.updateStep(sagaId, stepName, {
        status: 'completed',
        completedAt: new Date()
      });
    } catch (error) {
      await this.sagaRepository.updateStep(sagaId, stepName, {
        status: 'failed',
        error: error.message,
        failedAt: new Date()
      });
      throw error;
    }
  }

  private async compensate(sagaId: string): Promise<void> {
    const saga = await this.sagaRepository.findById(sagaId);

    // Execute compensating transactions in reverse order
    const completedSteps = saga.steps
      .filter(s => s.status === 'completed')
      .reverse();

    for (const step of completedSteps) {
      await this.compensateStep(sagaId, step.name);
    }

    await this.sagaRepository.update(sagaId, {
      status: 'compensated',
      compensatedAt: new Date()
    });
  }

  private async compensateStep(sagaId: string, stepName: string): Promise<void> {
    switch (stepName) {
      case 'reserve-inventory':
        await this.eventBus.publish({
          id: generateId(),
          type: 'inventory.release-requested',
          timestamp: new Date().toISOString(),
          version: '1.0',
          source: 'order-saga',
          correlationId: sagaId,
          metadata: {}
        });
        break;

      case 'process-payment':
        await this.eventBus.publish({
          id: generateId(),
          type: 'payment.refund-requested',
          timestamp: new Date().toISOString(),
          version: '1.0',
          source: 'order-saga',
          correlationId: sagaId,
          metadata: {}
        });
        break;

      case 'create-order':
        await this.eventBus.publish({
          id: generateId(),
          type: 'order.cancel-requested',
          timestamp: new Date().toISOString(),
          version: '1.0',
          source: 'order-saga',
          correlationId: sagaId,
          metadata: {}
        });
        break;
    }
  }
}
```

### Dead Letter Queue (DLQ) Handling

```typescript
// dlq-handler.service.ts
export class DLQHandler {
  private eventBus: EventBus;
  private alertService: AlertService;

  async processDLQ(dlqUrl: string): Promise<void> {
    const command = new ReceiveMessageCommand({
      QueueUrl: dlqUrl,
      MaxNumberOfMessages: 10,
      WaitTimeSeconds: 20
    });

    const response = await this.sqsClient.send(command);

    if (response.Messages) {
      for (const message of response.Messages) {
        try {
          const event = JSON.parse(message.Body!);

          // Log failed event
          logger.error('Event processing failed permanently', {
            event,
            receiveCount: message.Attributes?.ApproximateReceiveCount
          });

          // Alert team
          await this.alertService.sendAlert({
            severity: 'high',
            title: 'Event DLQ Processing Required',
            message: `Event ${event.type} failed permanently`,
            details: event
          });

          // Delete from DLQ after logging
          await this.sqsClient.send(
            new DeleteMessageCommand({
              QueueUrl: dlqUrl,
              ReceiptHandle: message.ReceiptHandle!
            })
          );
        } catch (error) {
          logger.error('DLQ processing error', { error });
        }
      }
    }
  }
}
```

### Infrastructure Configuration

```yaml
# terraform/event-bus.tf
resource "aws_sns_topic" "events" {
  name = "portfolio-events"

  tags = {
    Environment = var.environment
    Service     = "event-bus"
  }
}

resource "aws_sqs_queue" "order_events" {
  name                       = "order-events-queue"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600 # 14 days
  receive_wait_time_seconds  = 20
  visibility_timeout_seconds = 300

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_events_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Environment = var.environment
    Service     = "order-service"
  }
}

resource "aws_sqs_queue" "order_events_dlq" {
  name                      = "order-events-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Environment = var.environment
    Service     = "order-service"
  }
}

resource "aws_sns_topic_subscription" "order_events" {
  topic_arn = aws_sns_topic.events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.order_events.arn

  filter_policy = jsonencode({
    eventType = ["order.created", "order.paid", "order.shipped"]
  })
}
```

## Consequences

### Positive
- Loose coupling between services
- Asynchronous processing reduces latency
- Better scalability
- Event replay capabilities
- Audit trail through event log
- Resilience through retries and DLQ

### Negative
- Eventual consistency complexity
- Debugging distributed flows is harder
- Message ordering challenges
- Increased infrastructure complexity
- Potential duplicate message handling

### Mitigation
- Implement correlation IDs for tracing
- Use idempotency keys for duplicate handling
- Comprehensive event logging
- Saga pattern for distributed transactions
- DLQ monitoring and alerts
- Event schema versioning

## Performance Metrics
- Event processing latency: < 100ms (p95)
- Message throughput: 10,000 events/second
- Event replay time: < 5 minutes for full history
- DLQ rate: < 0.1%

## Implementation Checklist
- [x] Set up SNS topic for events
- [x] Create SQS queues for each service
- [x] Implement event bus service
- [x] Add event sourcing for critical workflows
- [x] Implement saga pattern
- [x] Set up DLQ handling
- [x] Add event monitoring and alerts
- [x] Document event schemas
- [x] Load test event processing

## Review Date
Review this decision in 6 months based on:
- Event processing performance
- Saga complexity
- Infrastructure costs
- Developer experience
- System reliability metrics
