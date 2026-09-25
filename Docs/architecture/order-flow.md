# Order Flow Architecture

## Objective

Build an event-driven order processing platform where order creation is separated from asynchronous order processing.

## Initial Flow

Client
  ↓
API Gateway
  ↓
Order API Lambda
  ↓
DynamoDB
  ↓
EventBridge
  ↓
SQS
  ↓
Order Processor Lambda
  ↓
DynamoDB

## Order Creation

The client sends an order to the API.

The API Lambda:

1. Validates the request.
2. Creates an order ID.
3. Stores the order in DynamoDB.
4. Publishes an order-created event.
5. Returns the order response.

## Asynchronous Processing

The order-created event is delivered through EventBridge to an SQS queue.

The Order Processor Lambda consumes messages from SQS and updates the order state in DynamoDB.

## Failure Handling

If processing fails:

SQS
  ↓
Lambda failure
  ↓
Retry
  ↓
Retry
  ↓
Retry
  ↓
Dead Letter Queue

CloudWatch will later be used for monitoring and alerting.

## Initial Order States

PENDING
PROCESSING
COMPLETED
FAILED

## Design Goal

The API should not need to wait for asynchronous order processing to complete.

The architecture should demonstrate:

- Event-driven architecture
- Asynchronous processing
- Queue-based decoupling
- Retry handling
- Dead Letter Queue
- Observability