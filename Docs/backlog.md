# Event-Driven Order Platform — Backlog

## Project Goal

Build a production-style AWS serverless order-processing platform demonstrating event-driven architecture, asynchronous processing, reliability, least-privilege IAM, infrastructure as code, CI/CD, observability, and failure recovery.

This project should complement the Cloud Native Test Platform rather than repeat its Kubernetes-focused architecture.

---

## Phase 0 — Project Foundation

- [ ] Create GitHub repository: `event-driven-order-platform`
- [ ] Create initial repository structure
- [ ] Add `README.md`
- [ ] Add `Docs/backlog.md`
- [ ] Add `.gitignore`
- [ ] Add project architecture overview
- [ ] Define AWS region and naming convention
- [ ] Create initial feature branch and PR workflow

**Acceptance:** Repository is clean, documented, and the backlog is committed.

---

## Phase 1 — Application Design

### Order API

- [ ] Define `POST /orders`
- [ ] Define `GET /orders/{order_id}`
- [ ] Define order request/response schemas
- [ ] Generate unique order IDs
- [ ] Define order states: `CREATED`, `PROCESSING`, `COMPLETED`, `FAILED`
- [ ] Define validation rules
- [ ] Define error responses
- [ ] Document the API contract

**Acceptance:** API contract and order lifecycle are documented.

---

## Phase 2 — Serverless Order API

### API Gateway

- [ ] Create API endpoint
- [ ] Configure `POST /orders`
- [ ] Configure `GET /orders/{order_id}`
- [ ] Configure Lambda integration
- [ ] Test deployed API

### Lambda

- [ ] Create Order API Lambda
- [ ] Implement validation
- [ ] Implement order creation
- [ ] Implement order retrieval
- [ ] Add structured logging
- [ ] Add unit tests

**Acceptance:** Orders can be created and retrieved through the API.

---

## Phase 3 — DynamoDB

- [ ] Create orders table
- [ ] Define partition key
- [ ] Define order attributes
- [ ] Configure appropriate capacity mode
- [ ] Configure encryption
- [ ] Implement persistence
- [ ] Implement retrieval
- [ ] Add error handling
- [ ] Add least-privilege IAM permissions

**Acceptance:** Orders are persisted and retrievable.

📸 **SCREENSHOT — DynamoDB table and sample order**

---

## Phase 4 — Event-Driven Architecture

### EventBridge

- [ ] Define `OrderCreated` event
- [ ] Define event schema
- [ ] Create event bus/rule
- [ ] Configure event target
- [ ] Publish event after successful order creation
- [ ] Test event delivery

Example:

```json
{
  "eventType": "OrderCreated",
  "orderId": "ORD-12345",
  "timestamp": "..."
}
```

**Acceptance:** Creating an order produces an `OrderCreated` event that is routed by EventBridge.

📸 **SCREENSHOT — EventBridge rule and target**

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
Lambda
     ↓
DynamoDB
     ↓
EventBridge
     ↓
SQS
     ↓
Processing Lambda
     ↓
DynamoDB
```

**Acceptance:** Order processing is asynchronous and successful messages are processed automatically.

📸 **SCREENSHOT — SQS queue and processing**

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

📸 **SCREENSHOT — Failed message in DLQ**

📸 **SCREENSHOT — CloudWatch DLQ alarm**

📸 **SCREENSHOT — Recovered order**

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

📸 **SCREENSHOT — Successful Step Functions execution**

📸 **SCREENSHOT — Failure/recovery execution**

---

## Phase 8 — IAM & Security

- [ ] Create dedicated IAM roles for Lambda functions
- [ ] Apply least-privilege permissions
- [ ] Restrict DynamoDB access
- [ ] Restrict SQS access
- [ ] Restrict EventBridge permissions
- [ ] Restrict Step Functions permissions
- [ ] Avoid hard-coded AWS credentials
- [ ] Use GitHub OIDC for CI/CD
- [ ] Review IAM policies
- [ ] Document security decisions

**Acceptance:** No static AWS credentials are stored in GitHub and workloads have only required permissions.

📸 **SCREENSHOT — IAM role/policy evidence**

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

📸 **SCREENSHOT — Final Terraform plan**

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

📸 **SCREENSHOT — Successful GitHub Actions pipeline**

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

📸 **SCREENSHOT — CloudWatch dashboard**

📸 **SCREENSHOT — CloudWatch application logs**

📸 **SCREENSHOT — CloudWatch alarms**

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
- [ ] Lambda → DynamoDB
- [ ] EventBridge → SQS
- [ ] SQS → Lambda
- [ ] Processing → DynamoDB

### End-to-End Test

- [ ] Create order
- [ ] Verify DynamoDB record
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
- [ ] Architecture diagram
- [ ] AWS service explanation
- [ ] Event flow explanation
- [ ] Order lifecycle diagram
- [ ] Failure/recovery diagram
- [ ] IAM/security explanation
- [ ] Terraform explanation
- [ ] CI/CD explanation
- [ ] Observability explanation
- [ ] Testing instructions
- [ ] Local development instructions
- [ ] Cost considerations
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

Every screenshot should prove something. Avoid collecting screenshots simply because an AWS console page exists.

---

# Final Definition of Done

- [ ] Client can create an order through the API
- [ ] Orders are stored in DynamoDB
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
- [ ] README and architecture documentation are complete
- [ ] Portfolio evidence has been collected

---

## Final Project Outcome

**Serverless Architecture + Event-Driven Design + Asynchronous Processing + Reliability + Security + Infrastructure as Code + CI/CD + Observability**

## Status

**NOT STARTED**

### Next recommended stage

**Phase 0 — Project Foundation**
