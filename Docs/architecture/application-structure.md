# Application Structure

## Overview

The application contains two primary Lambda functions:

1. Order API Lambda
2. Order Processor Lambda

The two functions have separate responsibilities.

## Order API Lambda

Flow:

```text
API Gateway
    ↓
Order API Lambda
    ↓
Validate request
    ↓
Generate orderId
    ↓
Create order
    ↓
Store in DynamoDB
    ↓
Publish OrderCreated event
    ↓
Return HTTP 202


The API Lambda handles synchronous order acceptance.

It does not perform the complete asynchronous order-processing workflow.

Order Processor Lambda

Flow:

EventBridge
    ↓
SQS
    ↓
Order Processor Lambda
    ↓
Process order
    ↓
Update DynamoDB

The processor handles asynchronous order processing.

