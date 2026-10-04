# Event-Driven Order Platform — Backlog

## Project Goal

Build a production-style AWS serverless order-processing platform demonstrating:

- Event-driven architecture
- Asynchronous processing
- Reliability and failure recovery
- Least-privilege IAM
- Infrastructure as Code
- CI/CD with GitHub Actions and OIDC
- Observability
- Idempotency
- Automated testing

---

# Phase 0 — Project Foundation

- [x] Create GitHub repository
- [x] Create repository structure
- [x] Add README
- [x] Add backlog
- [x] Add `.gitignore`
- [x] Define AWS region and naming convention
- [x] Establish PR workflow

**Status:** COMPLETE

---

# Phase 1 — Application Design

## Order API

- [x] Define `POST /orders`
- [x] Define order request/response schema
- [x] Generate backend order IDs
- [x] Define order states: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- [x] Define validation rules
- [x] Define error responses
- [x] Document API contract

## Architecture

- [x] Document synchronous HTTP response
- [x] Document asynchronous event flow
- [x] Document order data model
- [x] Document `OrderCreated` event contract
- [x] Document Lambda application structure

**Status:** COMPLETE

### Optional Future Enhancement

- [ ] Implement `GET /orders/{order_id}`

---

# Phase 2 — Serverless Order API

- [x] Create Order API Lambda
- [x] Parse API Gateway requests
- [x] Validate request body
- [x] Generate order ID
- [x] Generate UTC timestamp
- [x] Persist `PENDING` order
- [x] Return HTTP `202 Accepted`
- [x] Handle DynamoDB errors
- [x] Deploy API Gateway
- [x] Configure `POST /orders`
- [x] Deploy Lambda
- [x] Configure `dev` stage
- [x] Test deployed API

**Status:** COMPLETE

---

# Phase 3 — DynamoDB

- [x] Create `Orders` table
- [x] Configure `orderId` partition key
- [x] Configure on-demand capacity
- [x] Persist orders
- [x] Update order lifecycle state
- [x] Configure least-privilege access
- [x] Verify boto3 → DynamoDB integration
- [x] Verify application-generated orders

**Status:** COMPLETE

---

# Phase 4 — Event-Driven Architecture

## EventBridge V2

- [x] Define versioned `OrderCreated` event
- [x] Create custom EventBridge V2 event bus
- [x] Configure EventBridge V2 subscriber
- [x] Configure SQS target
- [x] Configure event filtering
- [x] Configure least-privilege `events:PutEvents`
- [x] Publish event after successful order creation
- [x] Verify event delivery
- [x] Test event filtering with integration test

### Verified Flow

```text
Order API Lambda
      ↓
EventBridge V2
      ↓
SQS OrderQueue
```

**Status:** COMPLETE

---

# Phase 5 — Asynchronous Processing

- [x] Create SQS processing queue
- [x] Create SQS DLQ
- [x] Configure redrive policy
- [x] Configure maximum receive count = 3
- [x] Configure EventBridge → SQS
- [x] Create Order Processor Lambda
- [x] Configure SQS → Lambda event source mapping
- [x] Parse EventBridge/SQS messages
- [x] Update order to `PROCESSING`
- [x] Start Step Functions workflow
- [x] Update order to `COMPLETED`
- [x] Verify successful end-to-end processing

### Verified Flow

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
Step Functions
     ↓
Order Worker Lambda
     ↓
DynamoDB — COMPLETED
```

**Status:** COMPLETE

---

# Phase 6 — DLQ & Failure Recovery

- [x] Implement controlled processor failure for testing
- [x] Configure SQS retries through redrive policy
- [x] Verify failed messages are retried
- [x] Verify message reaches DLQ after maximum receives
- [x] Create CloudWatch alarm for DLQ messages
- [x] Verify alarm enters `ALARM`
- [x] Remove controlled failure after testing
- [x] Replay/reprocess the failed message
- [x] Verify recovered order reaches `COMPLETED`
- [x] Verify data remains consistent
- [x] Document failure and recovery sequence

### Verified Failure Path

```text
Order Processor Lambda
        ↓
      FAIL
        ↓
   SQS retry #1
        ↓
   SQS retry #2
        ↓
   SQS retry #3
        ↓
       DLQ
        ↓
CloudWatch Alarm
        ↓
Recovery / Replay
        ↓
Order Processor
        ↓
Step Functions
        ↓
COMPLETED
```

**Status:** COMPLETE

---

# Phase 7 — Idempotency and Duplicate Events

- [x] Implement duplicate-event protection
- [x] Create `ProcessedOrderEvents` table
- [x] Claim events using conditional DynamoDB write
- [x] Prevent duplicate workflow processing
- [x] Handle duplicate execution
- [x] Test duplicate-event behavior
- [x] Verify business processing is not repeated
- [x] Verify order state remains consistent
- [x] Document at-least-once delivery implications

**Status:** COMPLETE

---

# Phase 8 — Step Functions

- [x] Define workflow
- [x] Add event-claim/idempotency state
- [x] Add processing state
- [x] Add completion state
- [x] Add duplicate-event path
- [x] Connect Order Processor to Step Functions
- [x] Connect Step Functions to Order Worker
- [x] Update order status
- [x] Verify successful execution
- [x] Document state machine

### Workflow

```text
ClaimEvent
    ↓
ProcessOrder
    ↓
CompleteOrder
    ↓
MarkEventCompleted
```

**Status:** COMPLETE

---

# Phase 9 — IAM & Security

- [x] Create dedicated IAM role for Order API Lambda
- [x] Create dedicated IAM role for Order Processor Lambda
- [x] Create dedicated IAM role for Order Worker Lambda
- [x] Restrict DynamoDB access
- [x] Restrict SQS access
- [x] Restrict EventBridge permissions
- [x] Restrict Step Functions permissions
- [x] Avoid hard-coded AWS credentials
- [x] Use GitHub OIDC for CI/CD
- [x] Restrict GitHub OIDC trust policy
- [x] Review project IAM policies
- [x] Document security decisions

**Status:** COMPLETE

---

# Phase 10 — Terraform / Infrastructure as Code

- [x] Configure AWS provider
- [x] Configure variables and outputs
- [x] Create DynamoDB resources
- [x] Create Lambda resources
- [x] Create API Gateway resources
- [x] Create EventBridge V2 resources
- [x] Create SQS/DLQ resources
- [x] Create Step Functions resources
- [x] Create IAM roles/policies
- [x] Configure Lambda application-code ownership
- [x] Run `terraform fmt`
- [x] Run `terraform validate`
- [x] Run Terraform plan/apply
- [x] Verify infrastructure
- [x] Prepare infrastructure for `terraform destroy`
- [x] Keep Terraform state local

### Terraform State Decision

Terraform state intentionally remains **local**.

A remote S3 backend was not added because this is a learning/portfolio environment and the infrastructure is intended to be destroyed after validation.

**Status:** COMPLETE

---

# Phase 11 — CI/CD

## Pull Request

- [x] Checkout repository
- [x] Setup runtime
- [x] Install dependencies
- [x] Run unit tests
- [x] Build Lambda deployment packages
- [x] Verify deployment packages
- [x] Run Terraform format check
- [x] Run Terraform validation

## Main Branch

- [x] Run tests
- [x] Validate Terraform
- [x] Authenticate to AWS using OIDC
- [x] Deploy Lambda application code
- [x] Run integration tests
- [x] Verify successful GitHub Actions deployment

### Deployment Model

Terraform manages infrastructure.

GitHub Actions manages Lambda application-code deployment.

Terraform ignores subsequent Lambda code artifact changes so application deployment remains independent from Terraform state.

**Status:** COMPLETE

---

# Phase 12 — Observability

- [x] Verify Lambda logging
- [x] Review API/processor CloudWatch logs
- [x] Monitor SQS processing
- [x] Monitor DLQ messages
- [x] Create/verify DLQ alarm
- [x] Verify DLQ alarm enters `ALARM`
- [x] Verify DLQ alarm returns to `OK`
- [x] Document operational signals

### Optional Future Enhancements

- [ ] CloudWatch dashboard
- [ ] Additional Lambda error alarms
- [ ] Additional API failure alarm

**Status:** COMPLETE for implemented observability scope

---

# Phase 13 — Automated Testing

## Unit Tests

- [x] Order validation
- [x] Order creation
- [x] Order Processor logic
- [x] Order Worker logic

**Result:** 21 unit tests passed

## Integration Tests

- [x] API validation
- [x] End-to-end order processing
- [x] Duplicate-event behavior
- [x] EventBridge filtering

**Result:** 10 integration tests passed

## Overall

**31 automated tests passed**

**Status:** COMPLETE

---

# Phase 14 — Reliability Testing

- [x] Test controlled Lambda failure
- [x] Test SQS retry behavior
- [x] Test DLQ behavior
- [x] Test CloudWatch alarm
- [x] Test recovery/replay
- [x] Verify recovered order reaches `COMPLETED`
- [x] Verify data remains consistent
- [x] Verify failure hook is removed after testing
- [x] Document observed behavior

**Status:** COMPLETE

---

# Phase 15 — Documentation

- [x] Final README
- [x] Architecture documentation
- [x] AWS service explanation
- [x] Event flow explanation
- [x] Order lifecycle documentation
- [x] Failure/recovery sequence
- [x] IAM/security explanation
- [x] Terraform explanation
- [x] CI/CD explanation
- [x] Observability explanation
- [x] Testing instructions
- [x] Local development instructions
- [x] Cost considerations
- [x] Lessons learned
- [x] Known limitations

**Status:** COMPLETE

---

# Phase 16 — Portfolio Evidence

- [x] Architecture
- [x] API request/response
- [x] DynamoDB order
- [x] EventBridge V2 routing
- [x] SQS queue
- [x] Order Processor logs
- [x] Controlled failure evidence
- [x] SQS retry evidence
- [x] DLQ failure evidence
- [x] CloudWatch alarm evidence
- [x] Step Functions workflow
- [x] IAM least-privilege implementation
- [x] Terraform validation
- [x] GitHub Actions success
- [x] Automated test results
- [x] Successful end-to-end order
- [x] Failure → retry → DLQ → recovery

**Status:** COMPLETE

---

# Final Definition of Done

- [x] Client can create an order through the API
- [x] Orders are stored in DynamoDB
- [x] `OrderCreated` events are published
- [x] Events are processed asynchronously through SQS
- [x] Processing updates order state
- [x] Failed messages are retried and verified
- [x] Failed messages reach the DLQ
- [x] CloudWatch detects the DLQ condition
- [x] Failed orders can be recovered/reprocessed
- [x] Step Functions demonstrates workflow orchestration
- [x] Current Lambda workloads follow least privilege
- [x] Infrastructure is managed through Terraform
- [x] CI/CD is automated through GitHub Actions
- [x] GitHub uses OIDC instead of static AWS credentials
- [x] CloudWatch provides logs, metrics, and alarms within the implemented scope
- [x] Automated unit and integration tests pass
- [x] Failure scenarios have been deliberately tested
- [x] Recovery has been verified
- [x] README and architecture documentation are complete
- [x] Portfolio evidence has been collected

---

# Final Project Outcome

**Serverless Architecture + Event-Driven Design + Asynchronous Processing + Reliability + Security + Infrastructure as Code + CI/CD + Observability + Idempotency + Automated Testing**

## Final Validation

- **21 unit tests passed**
- **10 integration tests passed**
- **31 total automated tests passed**
- Controlled failure verified
- SQS retry behavior verified
- DLQ behavior verified
- CloudWatch alarm verified
- DLQ recovery verified
- Recovered order reached `COMPLETED`
- Duplicate-event behavior verified
- Step Functions verified
- GitHub Actions CI/CD verified
- GitHub OIDC verified
- Terraform validated
- Least-privilege IAM implemented

## Deployment Status

The AWS environment is intentionally ephemeral.

After final validation, infrastructure can be removed with:

```bash
terraform destroy
```

Terraform state remains local.

The GitHub repository preserves the source code, infrastructure definitions, tests, CI/CD workflow, backlog, and documentation so the environment can be recreated later.

---

# Optional Future Enhancements

These are outside the completed project scope:

- `GET /orders/{order_id}`
- CloudWatch dashboard
- Additional operational alarms
- Additional API capabilities
- More complex Step Functions business workflows

These are enhancements rather than blockers for project completion.

---

# Final Status

## PROJECT COMPLETE

```text
31 automated tests passed

Failure → Retry → DLQ → Alarm → Recovery verified

Step Functions verified

Idempotency verified

Terraform validated

GitHub Actions CI/CD verified

GitHub OIDC verified

Least-privilege IAM implemented
```
