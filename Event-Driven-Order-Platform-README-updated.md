# Event-Driven Order Platform

A hands-on AWS serverless project focused on **event-driven architecture, asynchronous processing, reliability, least-privilege IAM, Infrastructure as Code, CI/CD, and observability**.

This project complements the completed Cloud Native Test Platform by focusing on AWS serverless and messaging patterns rather than Kubernetes.

## Current Status

**In progress — Phase 2 / Phase 3**

The current implementation has successfully built and tested the Order API logic locally and persisted orders to AWS DynamoDB.

### Completed so far

- Project repository foundation
- Application architecture and order-flow documentation
- Order request/response contract
- Order data model
- `OrderCreated` event contract
- Lambda handler structure
- API Gateway-style event simulation
- JSON request parsing
- Request validation
- Backend-generated order IDs
- UTC timestamps
- `PENDING` order creation
- HTTP `202 Accepted` response
- DynamoDB `Orders` table
- `orderId` partition key
- DynamoDB on-demand capacity
- Python `boto3` integration
- DynamoDB `PutItem` persistence
- DynamoDB error handling
- Environment-based table/region configuration
- Local AWS profile handling without hard-coding the profile in application code

### Not completed yet

- API Gateway deployment
- AWS Lambda deployment
- `GET /orders/{order_id}`
- EventBridge integration
- SQS processing
- DLQ and retry workflow
- Step Functions
- Production IAM roles
- Terraform infrastructure
- CI/CD
- CloudWatch observability
- Automated tests
- End-to-end reliability testing

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
EventBridge
  ↓
SQS
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

Lambda → OrderCreated event → EventBridge → SQS → Processor Lambda
```

The API does not wait for asynchronous processing to finish.

## Order Lifecycle

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure path:

```text
PENDING
   ↓
PROCESSING
   ↓
FAILED
```

`PENDING` means the order has been accepted and persisted but asynchronous processing has not completed.

## Current Order Model

Example DynamoDB item:

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

The application uses `orderId` as the partition key. Other order information is stored as item attributes.

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

The client does not provide:

- `orderId`
- `status`
- `createdAt`

The backend generates those values.

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

DynamoDB failures return `500` without exposing raw AWS errors to the client.

## Current Application Structure

```text
app/
├── functions/
│   └── order_api/
│       └── handler.py
├── models/
├── services/
└── requirements.txt
```

The current Lambda handler is being built incrementally before introducing the complete AWS API Gateway integration.

## Local Development

Install dependencies:

```powershell
python -m pip install -r app/requirements.txt
```

The application uses `boto3` for AWS access.

For local development, AWS credentials are supplied through the developer's AWS environment/profile rather than being hard-coded in application code.

Set the working profile for the current PowerShell session:

```powershell
$env:AWS_PROFILE="YOUR_PROFILE_NAME"
```

Run the current local Lambda simulation:

```powershell
python app/functions/order_api/handler.py
```

The local test simulates an API Gateway event, validates the order, writes it to DynamoDB, and returns `202`.

## AWS Services

Planned/current services:

| Service | Purpose | Status |
|---|---|---|
| API Gateway | Public order API | Planned |
| Lambda | Order API and processing | Order API logic built locally |
| DynamoDB | Order persistence | Implemented |
| EventBridge | Order event routing | Planned |
| SQS | Asynchronous buffering/retries | Planned |
| SQS DLQ | Failed-message isolation | Planned |
| Step Functions | Workflow orchestration | Planned |
| IAM | Least-privilege access | Planned |
| Terraform | Infrastructure as Code | Planned |
| GitHub Actions | CI/CD | Planned |
| CloudWatch | Logs, metrics, alarms | Planned |

## Event Contract

The planned `OrderCreated` event uses a versioned envelope:

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

The event is intended to contain the information needed by downstream consumers without coupling the producer directly to their implementation.

## Learning Goals

This project is intended to demonstrate practical understanding of:

- Serverless architecture
- Event-driven architecture
- Asynchronous messaging
- Lambda
- API Gateway
- DynamoDB
- EventBridge
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

Evidence will be collected later after meaningful milestones. Screenshots should demonstrate engineering outcomes rather than simply showing AWS console pages.

Planned evidence includes:

- API request/response
- DynamoDB order
- EventBridge routing
- SQS processing
- DLQ failure and recovery
- Step Functions execution
- IAM permissions
- Terraform plan
- CI/CD execution
- CloudWatch logs, metrics, and alarms
- End-to-end order processing

## Next Step

**Deploy the Order API Lambda to AWS and then place API Gateway in front of it.**

After the deployed API is working, the project will continue into the event-driven portion:

```text
Order API Lambda
  ↓
DynamoDB
  ↓
EventBridge
  ↓
SQS
  ↓
Order Processor Lambda
```
