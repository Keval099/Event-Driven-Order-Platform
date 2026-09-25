# Event Contracts

## OrderCreated

The `OrderCreated` event is published when an order has been successfully created and stored.

## Event Structure

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