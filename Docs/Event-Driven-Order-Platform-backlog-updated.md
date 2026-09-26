# Event-Driven Order Platform — Backlog

## Project Goal

Build a production-style AWS serverless order-processing platform demonstrating event-driven architecture, asynchronous processing, reliability, least-privilege IAM, infrastructure as code, CI/CD, observability, and failure recovery.

This project should complement the Cloud Native Test Platform rather than repeat its Kubernetes-focused architecture.

---

## Phase 0 — Project Foundation

- [x] Create GitHub repository: `event-driven-order-platform`
- [x] Create initial repository structure
- [x] Add `README.md`
- [x] Add `Docs/backlog.md`
- [x] Add `.gitignore`
- [x] Add project architecture overview
- [x] Define AWS region and naming convention
- [x] Create initial feature branch and PR workflow

**Acceptance:** Repository is clean, documented, and the backlog is committed.

**Status:** COMPLETE

---

## Phase 1 — Application Design

### Order API

- [x] Define `POST /orders`
- [ ] Define `GET /orders/{order_id}` — planned
- [x] Define order request/response schemas
- [x] Generate unique order IDs
- [x] Define order states: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- [x] Define validation rules
- [x] Define error responses
- [x] Document the API contract

### Architecture Decisions

- [x] Document synchronous HTTP response vs asynchronous event flow
- [x] Document order data model
- [x] Document `OrderCreated` event contract
- [x] Document Lambda application structure

**Acceptance:** API contract, order lifecycle, event contract, and application structure are documented.

**Status:** COMPLETE

---

## Phase 2 — Serverless Order API

### Lambda — Local Implementation

- [x] Create Order API Lambda handler
- [x] Simulate an API Gateway event locally
- [x] Parse JSON request body
- [x] Validate `customerId`
- [x] Validate `items`
- [x] Validate `productId`
- [x] Validate `quantity`
- [x] Generate backend order ID
- [x] Generate UTC creation timestamp
- [x] Create order with `PENDING` status
- [x] Return `202 Accepted`
- [x] Handle DynamoDB client errors

### API Gateway / AWS Deployment

- [ ] Create API endpoint
- [ ] Configure `POST /orders`
- [ ] Configure Lambda integration
- [ ] Deploy Lambda to AWS
- [ ] Configure Lambda environment variables
- [ ] Test deployed API

### Remaining Application Work

- [ ] Implement `GET /orders/{order_id}`
- [ ] Add structured logging
- [ ] Add unit tests

**Acceptance:** A deployed API can create and retrieve orders.

**Status:** IN PROGRESS

---

## Phase 3 — DynamoDB

- [x] Create `Orders` table
- [x] Define `orderId` as the partition key
- [x] Define `orderId` as String
- [x] Define order attributes
- [x] Configure on-demand capacity
- [x] Use the DynamoDB Standard table class
- [ ] Explicitly review/verify encryption configuration
- [x] Implement order persistence
- [ ] Implement order retrieval
- [x] Add DynamoDB error handling
- [ ] Add dedicated least-privilege IAM permissions for the application workload
- [x] Test Python → boto3 → DynamoDB
- [x] Verify application-generated orders in DynamoDB

**Current verified path:**

```text
Local Order API
      ↓
boto3
      ↓
DynamoDB Orders
      ↓
PutItem
      ↓
Order persisted
```

**Acceptance:** Orders are persisted and retrievable.

**Status:** IN PROGRESS

📸 **SCREENSHOT LATER — DynamoDB table and application-generated order**

---

## Phase 4 — Event-Driven Architecture

### EventBridge

- [x] Define `OrderCreated` event
- [x] Define event schema/version
- [ ] Create event bus/rule
- [ ] Configure event target
- [ ] Publish event after successful order creation
- [ ] Test event delivery

Example:

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

**Acceptance:** Creating an order produces an `OrderCreated` event that is routed by EventBridge.

📸 **SCREENSHOT LATER — EventBridge rule and target**

---

## Phase 5 — Asynchronous Processing with SQS

- [ ] Create order-processing SQS queue
- [ ] Configure visibility timeout
- [ ] Create dead-letter queue
- [ ] Configure redrive policy
- [ ] Connect EventBridge to SQS
- [ ] Create processing Lambda
- [ ] Configure SQS → Lambda event source mapping
- [ ] Update order to `PROCESSING`
- [ ] Update order to `COMPLETED`
- [ ] Add processing error handling

Target flow:

```text
POST /orders
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

**Acceptance:** Order processing is asynchronous and successful messages are processed automatically.

📸 **SCREENSHOT LATER — SQS queue and processing**

---

## Phase 6 — DLQ & Failure Recovery

This is a core learning objective.

- [ ] Implement intentional failure condition for testing
- [ ] Configure SQS retries
- [ ] Verify failed messages are retried
- [ ] Verify messages reach DLQ
- [ ] Create CloudWatch alarm for DLQ messages
- [ ] Fix the processing failure
- [ ] Replay/reprocess the failed message
- [ ] Verify order reaches `COMPLETED`
- [ ] Document the failure and recovery sequence

Failure demonstration:

```text
OrderCreated
     ↓
SQS
     ↓
Processing Lambda ❌
     ↓
Retry
     ↓
Retry
     ↓
Retry
     ↓
DLQ
     ↓
CloudWatch Alarm
```

Recovery:

```text
Fix processor
     ↓
Replay message
     ↓
Processing Lambda
     ↓
DynamoDB
     ↓
COMPLETED
```

📸 **SCREENSHOT LATER — Failed message in DLQ**

📸 **SCREENSHOT LATER — CloudWatch DLQ alarm**

📸 **SCREENSHOT LATER — Recovered order**

---

## Phase 7 — Step Functions

Use Step Functions for a focused order workflow.

- [ ] Define workflow
- [ ] Add validation state
- [ ] Add inventory simulation state
- [ ] Add payment simulation state
- [ ] Add success path
- [ ] Add failure path
- [ ] Add retry/error handling
- [ ] Update order status
- [ ] Document state machine

Target workflow:

```text
Validate Order
      ↓
Check Inventory
      ↓
Process Payment
      ↓
Update Order
      ↓
Order Completed
```

Failure:

```text
Process Payment
      ↓
FAILED
      ↓
Cancel Order
```

**Acceptance:** Both successful and failure executions can be demonstrated.

📸 **SCREENSHOT LATER — Successful Step Functions execution**

📸 **SCREENSHOT LATER — Failure/recovery execution**

---

## Phase 8 — IAM & Security

- [ ] Create dedicated IAM roles for Lambda functions
- [ ] Apply least-privilege permissions
- [ ] Restrict DynamoDB access
- [ ] Restrict SQS access
- [ ] Restrict EventBridge permissions
- [ ] Restrict Step Functions permissions
- [x] Avoid hard-coded AWS credentials in application code
- [ ] Use GitHub OIDC for CI/CD
- [ ] Review IAM policies
- [ ] Document security decisions

**Acceptance:** No static AWS credentials are stored in GitHub and workloads have only required permissions.

📸 **SCREENSHOT LATER — IAM role/policy evidence**

---

## Phase 9 — Terraform / Infrastructure as Code

- [ ] Configure AWS provider
- [ ] Configure variables and outputs
- [ ] Create DynamoDB resources
- [ ] Create Lambda resources
- [ ] Create API Gateway resources
- [ ] Create EventBridge resources
- [ ] Create SQS/DLQ resources
- [ ] Create Step Functions resources
- [ ] Create IAM roles/policies
- [ ] Create CloudWatch alarms
- [ ] Run `terraform fmt`
- [ ] Run `terraform validate`
- [ ] Run final `terraform plan`
- [ ] Document infrastructure

**Acceptance:** Core infrastructure is reproducible through Terraform.

📸 **SCREENSHOT LATER — Final Terraform plan**

---

## Phase 10 — CI/CD

### Pull Request

- [ ] Checkout repository
- [ ] Setup runtime
- [ ] Install dependencies
- [ ] Run unit tests
- [ ] Run linting
- [ ] Run Terraform format check
- [ ] Run Terraform validation

### Main Branch

- [ ] Run tests
- [ ] Validate Terraform
- [ ] Authenticate to AWS using OIDC
- [ ] Deploy application/infrastructure
- [ ] Run API smoke tests
- [ ] Report deployment status

Target:

```text
Git Push
   ↓
GitHub Actions
   ↓
Tests
   ↓
Terraform Validation
   ↓
AWS OIDC
   ↓
Deployment
   ↓
Smoke Test
```

**Acceptance:** PR validation and main-branch deployment are automated without static AWS credentials.

📸 **SCREENSHOT LATER — Successful GitHub Actions pipeline**

---

## Phase 11 — Observability

Use CloudWatch to monitor the serverless system.

- [ ] Configure Lambda logging
- [ ] Review API Gateway metrics/logs
- [ ] Monitor Lambda errors
- [ ] Monitor Lambda duration
- [ ] Monitor SQS messages
- [ ] Monitor DLQ messages
- [ ] Create CloudWatch dashboard
- [ ] Create Lambda error alarm
- [ ] Create DLQ alarm
- [ ] Create API failure alarm where appropriate
- [ ] Document operational signals

Dashboard targets:

```text
Orders Created
Orders Completed
Lambda Errors
Lambda Duration
SQS Messages
DLQ Messages
API Errors
```

📸 **SCREENSHOT LATER — CloudWatch dashboard**

📸 **SCREENSHOT LATER — CloudWatch application logs**

📸 **SCREENSHOT LATER — CloudWatch alarms**

---

## Phase 12 — Testing

### Unit Tests

- [ ] Order validation
- [ ] Order creation
- [ ] Order retrieval
- [ ] Event generation
- [ ] Processing Lambda
- [ ] Failure path

### Integration Tests

- [ ] API → Lambda
- [x] Lambda → DynamoDB
- [ ] EventBridge → SQS
- [ ] SQS → Lambda
- [ ] Processing → DynamoDB

### End-to-End Test

- [ ] Create order
- [x] Verify DynamoDB record
- [ ] Verify event
- [ ] Verify SQS processing
- [ ] Verify final status
- [ ] Verify CloudWatch logs

**Acceptance:** A complete order travels automatically from API request to `COMPLETED`.

---

## Phase 13 — Reliability Testing

- [ ] Test duplicate message/event behavior
- [ ] Test Lambda failure
- [ ] Test SQS retry behavior
- [ ] Test DLQ behavior
- [ ] Test Step Functions failure path
- [ ] Test recovery
- [ ] Verify data remains consistent
- [ ] Document observed behavior

---

## Phase 14 — Documentation

- [ ] Final README
- [x] Architecture documentation
- [x] AWS service explanation in working documentation
- [x] Event flow explanation
- [x] Order lifecycle documentation
- [ ] Failure/recovery diagram
- [ ] IAM/security explanation
- [ ] Terraform explanation
- [ ] CI/CD explanation
- [ ] Observability explanation
- [ ] Testing instructions
- [x] Local development instructions
- [x] Cost considerations
- [ ] Lessons learned
- [ ] Known limitations

---

## Phase 15 — Portfolio Evidence

Collect only evidence that proves an engineering outcome.

- [ ] Architecture diagram
- [ ] API request/response
- [ ] DynamoDB order
- [ ] EventBridge rule
- [ ] SQS queue
- [ ] DLQ failure
- [ ] Step Functions workflow
- [ ] IAM least-privilege evidence
- [ ] Terraform plan
- [ ] GitHub Actions success
- [ ] CloudWatch dashboard
- [ ] CloudWatch alarms
- [ ] Successful end-to-end order
- [ ] Failure → retry → DLQ → recovery

### Evidence Rule

Screenshots are intentionally collected later, after meaningful milestones. Every screenshot should prove an engineering outcome rather than simply showing an AWS console page.

---

# Final Definition of Done

- [ ] Client can create an order through the API
- [x] Orders are stored in DynamoDB
- [ ] `OrderCreated` events are published
- [ ] Events are processed asynchronously through SQS
- [ ] Processing updates order state
- [ ] Failed messages are retried
- [ ] Failed messages reach the DLQ
- [ ] CloudWatch detects the DLQ condition
- [ ] Failed orders can be recovered/reprocessed
- [ ] Step Functions demonstrates workflow orchestration
- [ ] IAM follows least privilege
- [ ] Infrastructure is managed through Terraform
- [ ] CI/CD is automated through GitHub Actions
- [ ] GitHub uses OIDC instead of static AWS credentials
- [ ] CloudWatch provides logs, metrics, and alarms
- [ ] Unit, integration, and end-to-end tests pass
- [ ] Failure scenarios have been deliberately tested
- [x] README and architecture documentation are being maintained
- [ ] Portfolio evidence has been collected

---

## Final Project Outcome

**Serverless Architecture + Event-Driven Design + Asynchronous Processing + Reliability + Security + Infrastructure as Code + CI/CD + Observability**

## Current Status

**IN PROGRESS — Phase 2 / Phase 3**

### Next recommended stage

**Deploy the Order API Lambda to AWS, then connect API Gateway.**
