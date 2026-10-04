resource "aws_dynamodb_table" "orders" {
  name         = "Orders"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "orderId"

  attribute {
    name = "orderId"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderPersistence"
  }
}

resource "aws_dynamodb_table" "processed_order_events" {
  name         = "ProcessedOrderEvents"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "Idempotency"
  }
}