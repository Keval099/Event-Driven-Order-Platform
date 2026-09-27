# Event-Driven Order Platform — Backlog

## Project Goal

Build a production-style AWS serverless order-processing platform demonstrating event-driven architecture, asynchronous processing, reliability, least-privilege IAM, infrastructure as code, CI/CD, observability, and failure recovery.

---

## Phase 0 — Project Foundation

- [x] Create GitHub repository
- [x] Create initial repository structure
- [x] Add README
- [x] Add backlog
- [x] Add `.gitignore`
- [x] Add architecture documentation
- [x] Define AWS region and naming convention
- [x] Create initial branch and PR workflow

**Status:** COMPLETE

---

## Phase 1 — Application Design

### Order API

- [x] Define `POST /orders`
- [ ] Define `GET /orders/{order_id}`
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

**Status:** COMPLETE

---

## Phase 2 — Serverless Order API

### Lambda

- [x] Create Order API Lambda handler
- [x] Simulate API Gateway event locally
- [x] Parse JSON request body
- [x] Validate request
- [x] Generate backend order ID
- [x] Generate UTC timestamp
- [x] Create `PENDING` order
- [x] Return `202 Accepted`
- [x] Handle DynamoDB errors

### API Gateway / AWS Deployment

- [x] Create API endpoint
- [x] Configure `POST /orders`
- [x] Configure Lambda proxy integration
- [x] Deploy Order API Lambda
- [x] Configure Lambda environment variables
- [x] Deploy `dev` stage
- [x] Test deployed API with real HTTP request

### Remaining Application Work

- [ ] Implement `GET /orders/{order_id}`
- [ ] Add structured logging
- [ ] Add unit tests

**Status:** COMPLETE for `POST /orders`; remaining GET/tests pending.

---

## Phase 3 — DynamoDB

- [x] Create `Orders` table
- [x] Define `orderId` as partition key
- [x] Define `orderId` as String
- [x] Define order attributes
- [x] Configure on-demand capacity
- [x] Implement order persistence
- [ ] Implement order retrieval
- [x] Add DynamoDB error handling
- [x] Configure least-privilege DynamoDB permissions
- [x] Test Python → boto3 → DynamoDB
- [x] Verify application-generated orders
- [ ] Explicitly review/verify encryption configuration

**Status:** IN PROGRESS — retrieval and final security review remain.

---

## Phase 4 — Event-Driven Architecture

### EventBridge V2

- [x] Define `OrderCreated` event
- [x] Define event schema/version
- [x] Create custom EventBridge V2 event bus
- [x] Configure EventBridge V2 subscriber
- [x] Configure SQS target
- [x] Configure event filtering
- [x] Grant least-privilege `events:PutEvents`
- [x] Publish event after successful order creation
- [x] Test event delivery

**Verified flow:**

```text
Order API Lambda
      ↓
EventBridge V2
      ↓
OrderQueue
```

**Status:** COMPLETE

---

## Phase 5 — Asynchronous Processing with SQS

- [x] Create order-processing SQS queue
- [x] Configure SQS dead-letter queue
- [x] Configure redrive policy
- [x] Configure maximum receives = 3
- [x] Connect EventBridge V2 to SQS
- [x] Create Order Processor Lambda
- [x] Configure SQS → Lambda event source mapping
- [x] Parse SQS/EventBridge message
- [x] Update order to `PROCESSING`
- [x] Update order to `COMPLETED`
- [x] Verify successful end-to-end processing
- [ ] Add controlled processing failure test

**Verified flow:**

```text
POST /orders
     ↓
API Gateway
     ↓
Order API Lambda
     ↓
DynamoDB — PENDING
     ↓
EventBridge V2
     ↓
SQS
     ↓
Order Processor Lambda
     ↓
DynamoDB — PROCESSING
     ↓
DynamoDB — COMPLETED
```

**Status:** COMPLETE for successful processing; failure testing remains.

---

## Phase 6 — DLQ & Failure Recovery

- [ ] Implement intentional failure condition for testing
- [x] Configure SQS retries through redrive policy
- [ ] Verify failed messages are retried
- [ ] Verify message reaches DLQ after maximum receives
- [ ] Create CloudWatch alarm for DLQ messages
- [ ] Fix the processing failure
- [ ] Replay/reprocess the failed message
- [ ] Verify recovered order reaches `COMPLETED`
- [ ] Document failure and recovery sequence

**Status:** NEXT

---

## Phase 7 — Idempotency and Duplicate Events

- [ ] Use `eventId` as the idempotency identifier
- [ ] Decide idempotency storage strategy
- [ ] Prevent duplicate business processing
- [ ] Test duplicate SQS delivery
- [ ] Verify order state remains consistent
- [ ] Document at-least-once delivery implications

**Status:** PLANNED

---

## Phase 8 — Step Functions

- [ ] Define workflow
- [ ] Add validation state
- [ ] Add inventory simulation state
- [ ] Add payment simulation state
- [ ] Add success path
- [ ] Add failure path
- [ ] Add retry/error handling
- [ ] Update order status
- [ ] Document state machine

Target:

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

**Status:** PLANNED

---

## Phase 9 — IAM & Security

- [x] Create dedicated IAM role for Order API Lambda
- [x] Create dedicated IAM role for Order Processor Lambda
- [x] Restrict DynamoDB access
- [x] Restrict SQS access
- [x] Restrict EventBridge permissions
- [ ] Restrict Step Functions permissions
- [x] Avoid hard-coded AWS credentials
- [ ] Use GitHub OIDC for CI/CD
- [ ] Review all IAM policies
- [ ] Document security decisions
- [ ] Review DynamoDB encryption configuration

**Status:** IN PROGRESS

---

## Phase 10 — Terraform / Infrastructure as Code

- [ ] Configure AWS provider
- [ ] Configure variables and outputs
- [ ] Create DynamoDB resources
- [ ] Create Lambda resources
- [ ] Create API Gateway resources
- [ ] Create EventBridge V2 resources
- [ ] Create SQS/DLQ resources
- [ ] Create Step Functions resources
- [ ] Create IAM roles/policies
- [ ] Create CloudWatch alarms
- [ ] Run `terraform fmt`
- [ ] Run `terraform validate`
- [ ] Run final `terraform plan`
- [ ] Document infrastructure

**Status:** PLANNED

---

## Phase 11 — CI/CD

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
- [ ] Deploy infrastructure/application
- [ ] Run API smoke tests
- [ ] Report deployment status

**Status:** PLANNED

---

## Phase 12 — Observability

- [x] Verify Lambda logging
- [x] Review API/processor CloudWatch logs
- [ ] Monitor Lambda errors
- [ ] Monitor Lambda duration
- [ ] Monitor SQS messages
- [ ] Monitor DLQ messages
- [ ] Create CloudWatch dashboard
- [ ] Create Lambda error alarm
- [ ] Create DLQ alarm
- [ ] Create API failure alarm where appropriate
- [ ] Document operational signals

**Status:** IN PROGRESS

---

## Phase 13 — Testing

### Unit Tests

- [ ] Order validation
- [ ] Order creation
- [ ] Order retrieval
- [ ] Event generation
- [ ] Processing Lambda
- [ ] Failure path

### Integration Tests

- [x] API → Lambda
- [x] Lambda → DynamoDB
- [x] EventBridge V2 → SQS
- [x] SQS → Lambda
- [x] Processing → DynamoDB

### End-to-End Test

- [x] Create order
- [x] Verify DynamoDB record
- [x] Verify event delivery
- [x] Verify SQS processing
- [x] Verify final `COMPLETED` status
- [x] Verify CloudWatch processor logs

**Status:** IN PROGRESS — automated tests remain.

---

## Phase 14 — Reliability Testing

- [ ] Test duplicate message/event behavior
- [ ] Test Lambda failure
- [ ] Test SQS retry behavior
- [ ] Test DLQ behavior
- [ ] Test Step Functions failure path
- [ ] Test recovery
- [ ] Verify data remains consistent
- [ ] Document observed behavior

**Status:** NEXT after DLQ implementation test.

---

## Phase 15 — Documentation

- [ ] Final README
- [x] Architecture documentation
- [x] AWS service explanation
- [x] Event flow explanation
- [x] Order lifecycle documentation
- [ ] Failure/recovery diagram
- [x] IAM/security explanation started
- [ ] Terraform explanation
- [ ] CI/CD explanation
- [ ] Observability explanation
- [ ] Testing instructions
- [x] Local development instructions
- [x] Cost considerations
- [ ] Lessons learned
- [ ] Known limitations

**Status:** IN PROGRESS

---

## Phase 16 — Portfolio Evidence

- [ ] Architecture diagram
- [ ] API request/response
- [ ] DynamoDB order
- [ ] EventBridge V2 routing
- [ ] SQS queue
- [ ] Order Processor logs
- [ ] DLQ failure
- [ ] CloudWatch alarm
- [ ] Step Functions workflow
- [ ] IAM least-privilege evidence
- [ ] Terraform plan
- [ ] GitHub Actions success
- [ ] CloudWatch dashboard
- [ ] Successful end-to-end order
- [ ] Failure → retry → DLQ → recovery

**Status:** PLANNED

---

# Final Definition of Done

- [x] Client can create an order through the API
- [x] Orders are stored in DynamoDB
- [x] `OrderCreated` events are published
- [x] Events are processed asynchronously through SQS
- [x] Processing updates order state
- [ ] Failed messages are retried and verified
- [ ] Failed messages reach the DLQ
- [ ] CloudWatch detects the DLQ condition
- [ ] Failed orders can be recovered/reprocessed
- [ ] Step Functions demonstrates workflow orchestration
- [x] Current Lambda workloads follow least privilege
- [ ] Infrastructure is managed through Terraform
- [ ] CI/CD is automated through GitHub Actions
- [ ] GitHub uses OIDC instead of static AWS credentials
- [ ] CloudWatch provides dashboards, metrics, and alarms
- [ ] Automated unit, integration, and end-to-end tests pass
- [ ] Failure scenarios have been deliberately tested
- [x] README and architecture documentation are being maintained
- [ ] Portfolio evidence has been collected

---

## Current Project Outcome

**Serverless Architecture + Event-Driven Design + Asynchronous Processing + Reliability + Security + Infrastructure as Code + CI/CD + Observability**

**Current milestone:** Core API → EventBridge V2 → SQS → Processor → DynamoDB flow is working and the successful `COMPLETED` lifecycle has been verified.

**Next recommended stage:** Controlled processor failure → SQS retries → DLQ → CloudWatch alarm → recovery.
