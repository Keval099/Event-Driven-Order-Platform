resource "aws_sqs_queue" "order_dlq" {
  name = "EventDrivenOrderPlatform-OrderDLQ"

  max_message_size = 1048576

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "DeadLetterQueue"
  }
}

resource "aws_sqs_queue" "order_queue" {
  name = "EventDrivenOrderPlatform-OrderQueue"

  max_message_size           = 1048576
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderProcessingQueue"
  }
}