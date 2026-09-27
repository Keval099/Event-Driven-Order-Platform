# Event-Driven Order Platform

A hands-on AWS serverless project focused on **event-driven architecture, asynchronous processing, reliability, least-privilege IAM, Infrastructure as Code, CI/CD, and observability**.

This project complements the completed Cloud Native Test Platform by focusing on AWS serverless and messaging patterns rather than Kubernetes.

## Current Status

**IN PROGRESS — Core event-driven processing path implemented and verified**

The main asynchronous order-processing path is now working end-to-end in AWS.

### Completed and verified

- Project repository foundation
- Application architecture and order-flow documentation
- Order request/response contract
- Order data model
- Versioned `OrderCreated` event contract
- Order API Lambda
- API Gateway REST API
- `POST /orders` deployed to `dev`
- API Gateway → Lambda proxy integration
- Request validation
- Backend-generated order IDs
- UTC timestamps
- `PENDING` order creation
- HTTP `202 Accepted` response
- DynamoDB `Orders` table with `orderId` partition key
- DynamoDB on-demand capacity
- DynamoDB persistence and error handling
- Least-privilege IAM for Order API DynamoDB access
- Custom EventBridge V2 event bus
- EventBridge V2 subscriber to SQS
- `OrderCreated` event publishing from Lambda
- Least-privilege `events:PutEvents` permission for the V2 bus
- SQS order-processing queue
- SQS dead-letter queue
- SQS redrive policy with maximum receives configured to `3`
- Order Processor Lambda
- Least-privilege SQS and DynamoDB permissions for the processor
- SQS → Lambda event source mapping
- Event parsing from the SQS/EventBridge message
- `PENDING → PROCESSING → COMPLETED` order lifecycle
- Successful end-to-end order processing verified in DynamoDB
- `boto3==1.43.102` pinned for Lambda packaging
- Lambda deployment artifacts excluded from Git
- Controlled processor failure test using `CUST-FAIL-TEST`
- SQS retry behavior verified with receive counts `1 → 2 → 3`
- Failed message verified in the SQS DLQ
- CloudWatch DLQ alarm verified transitioning to `ALARM`
- Failed processor code restored and redeployed
- DLQ message redriven to the source queue
- Failed order successfully recovered to `COMPLETED`
- DLQ verified empty after recovery
- CloudWatch DLQ alarm verified returning to `OK`

### Not completed yet

- `GET /orders/{order_id}`
- Idempotency implementation using `eventId`
- Step Functions workflow
- Terraform infrastructure
- CI/CD with GitHub Actions/OIDC
- CloudWatch dashboard and operational alarms
- Automated unit/integration/end-to-end tests
- Final portfolio evidence
- Final documentation and lessons learned

## Target Architecture

```text
Client
  ↓
API Gateway
  ↓
Order API Lambda
  ↓
DynamoDB
  ↓
EventBridge V2
  ↓
SQS OrderQueue
  ↓
Order Processor Lambda
  ↓
DynamoDB
```

Failure path:

```text
SQS
  ↓
Order Processor Lambda ❌
  ↓
SQS retry
  ↓
Retry
  ↓
Retry
  ↓
DLQ
  ↓
CloudWatch Alarm
```

The API response is deliberately separate from the event-driven processing path:

```text
Lambda → HTTP 202 response → Client

Lambda → OrderCreated event → EventBridge V2 → SQS → Processor Lambda
```

The API does not wait for asynchronous processing to finish.

## Current Verified Flow

```text
POST /orders
      ↓
API Gateway
      ↓
Order API Lambda
      ├── DynamoDB: PENDING
      │
      └── OrderCreated event
              ↓
        EventBridge V2
              ↓
          SQS Queue
              ↓
      Order Processor Lambda
              ├── PENDING → PROCESSING
              └── PROCESSING → COMPLETED
                       ↓
                   DynamoDB
```

A real order has been verified reaching `COMPLETED` in DynamoDB.

## Order Lifecycle

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure/recovery path verified in AWS:

```text
PENDING
   ↓
Processor failure
   ↓
SQS retries
   ↓
DLQ
   ↓
Redrive
   ↓
PROCESSING
   ↓
COMPLETED
```

The controlled failure test intentionally failed before the `PENDING → PROCESSING` update, so the failed test order remained `PENDING` until it was redriven and successfully processed.

`PENDING` means the order has been accepted and persisted but asynchronous processing has not completed.

## Current Order Model

```json
{
  "orderId": "ORD-12345",
  "customerId": "CUST-001",
  "items": [
    {
      "productId": "PROD-001",
      "quantity": 2
    }
  ],
  "status": "PENDING",
  "createdAt": "2026-09-26T08:00:00Z"
}
```

DynamoDB design:

```text
Table: Orders
Partition key: orderId
Type: String
Capacity mode: On-demand
```

## API Contract

### Request

```http
POST /orders
```

```json
{
  "customerId": "CUST-001",
  "items": [
    {
      "productId": "PROD-001",
      "quantity": 2
    }
  ]
}
```

The client does not provide `orderId`, `status`, or `createdAt`.

### Successful response

```http
202 Accepted
```

```json
{
  "orderId": "ORD-12345",
  "status": "PENDING",
  "message": "Order accepted"
}
```

### Validation

The API validates:

- `customerId` is present and non-empty
- `items` is a non-empty list
- every item is an object
- `productId` is present and non-empty
- `quantity` is an integer greater than zero

Invalid requests return `400`.

## Event Contract

The application event uses a versioned envelope:

```json
{
  "eventId": "evt-123456",
  "eventType": "OrderCreated",
  "eventVersion": "1.0",
  "occurredAt": "2026-09-25T10:30:00Z",
  "data": {
    "orderId": "ORD-12345",
    "customerId": "CUST-001"
  }
}
```

The event is published to the custom **EventBridge V2** bus and routed to SQS through an EventBridge V2 subscriber.

The SQS message observed by the processor contains the EventBridge envelope, with the application event available under `detail`.

## Current Application Structure

```text
app/
├── functions/
│   ├── order_api/
│   │   └── handler.py
│   └── order_processor/
│       └── handler.py
├── models/
├── services/
└── requirements.txt
```

Current dependency:

```text
boto3==1.43.102
```

The pinned boto3 version is packaged into the Lambda deployment ZIPs so the Lambda functions can use the required AWS SDK functionality.

Build artifacts such as `lambda-package/`, `processor-package/`, `order-api.zip`, and `order-processor.zip` are excluded through `.gitignore`.

## AWS Services

| Service | Purpose | Status |
|---|---|---|
| API Gateway | Public order API | Implemented |
| Lambda | Order API and asynchronous processing | Implemented |
| DynamoDB | Order persistence and lifecycle state | Implemented |
| EventBridge V2 | Event routing | Implemented |
| SQS | Asynchronous buffering and retries | Implemented |
| SQS DLQ | Failed-message isolation | Implemented and failure/recovery verified |
| IAM | Least-privilege workload permissions | Implemented for current Lambdas |
| CloudWatch | Logs and operational visibility | Logs and DLQ alarm verified; dashboard pending |
| Step Functions | Workflow orchestration | Planned |
| Terraform | Infrastructure as Code | Planned |
| GitHub Actions | CI/CD | Planned |

## IAM Design

The project uses separate execution roles.

### Order API Lambda

Current permissions include:

- `dynamodb:PutItem` on the `Orders` table
- `events:PutEvents` on the specific EventBridge V2 bus

### Order Processor Lambda

Current permissions include:

- `sqs:ReceiveMessage`
- `sqs:DeleteMessage`
- `sqs:GetQueueAttributes`
- `dynamodb:UpdateItem` on the `Orders` table

Broad service permissions such as `sqs:*`, `dynamodb:*`, or `events:*` are intentionally avoided.

## Learning Goals

This project demonstrates practical understanding of:

- Serverless architecture
- Event-driven architecture
- Asynchronous messaging
- Lambda
- API Gateway
- DynamoDB
- EventBridge V2
- SQS
- DLQs and retries
- Step Functions
- IAM least privilege
- Terraform
- GitHub Actions
- CloudWatch
- Idempotency and duplicate-event considerations
- Failure recovery

## Evidence

Evidence will be collected after meaningful milestones.

Planned evidence includes:

- API request/response
- DynamoDB `PENDING` order
- EventBridge V2 event routing
- SQS message delivery
- Order Processor logs
- `PROCESSING → COMPLETED` DynamoDB update
- DLQ failure and recovery
- Step Functions execution
- IAM permissions
- Terraform plan
- CI/CD execution
- CloudWatch logs, metrics, and alarms
- End-to-end order processing

## Verified Reliability Test

The failure and recovery path has now been deliberately tested in AWS.

```text
CUST-FAIL-TEST
      ↓
Processor Lambda intentionally fails
      ↓
SQS receive count: 1 → 2 → 3
      ↓
DLQ
      ↓
CloudWatch alarm → ALARM
      ↓
Failure condition removed and processor redeployed
      ↓
DLQ redrive
      ↓
PROCESSING → COMPLETED
      ↓
DLQ = 0
      ↓
CloudWatch alarm → OK
```

This demonstrates controlled failure, SQS retry behavior, DLQ isolation, operational alerting, and recovery/replay.

## Evidence

Verified evidence now includes:

- API request/response
- DynamoDB `PENDING` order
- EventBridge V2 event routing
- SQS delivery
- Order Processor failure logs
- SQS receive counts `1 → 2 → 3`
- DLQ containing the failed message
- CloudWatch DLQ alarm in `ALARM`
- Successful redrive/recovery
- `PROCESSING → COMPLETED` recovery
- DLQ returning to `0`
- CloudWatch alarm returning to `OK`

Still planned:

- Step Functions execution
- IAM permissions evidence
- Terraform plan
- CI/CD execution
- CloudWatch dashboard
- Final portfolio evidence package
- Final documentation and lessons learned

## Next Stage

The next engineering milestone is **idempotency and duplicate-event handling** using the existing versioned `eventId`.
