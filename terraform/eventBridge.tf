resource "awscc_eventsv2_event_bus" "orders" {
  name        = "EventDrivenOrderPlatform-Bus"
  description = "Event bus for the Event-Driven Order Platform"

  tags = [
    {
      key   = "Project"
      value = var.project_name
    },
    {
      key   = "Environment"
      value = var.environment
    },
    {
      key   = "Component"
      value = "EventBus"
    }
  ]
}

resource "awscc_eventsv2_subscriber" "order_created_to_sqs" {
  name          = "EventDrivenOrderPlatform-OrderCreatedToSQS"
  event_bus_arn = awscc_eventsv2_event_bus.orders.event_bus_arn

  invoke_configuration = {
    target_arn = aws_sqs_queue.order_queue.arn
    role_arn   = "arn:aws:iam::825765413460:role/service-role/Amazon_EventBridge_V2_Invoke_Sqs_1554510381"
  }

  filter_configuration = {
    filters = [
      {
        pattern = jsonencode({
          source = [
            "event-driven-order-platform.orders"
          ]

          "detail-type" = [
            "OrderCreated"
          ]
        })

        scope = "DATA"
      }
    ]
  }

  batch_configuration = {
    max_batch_size              = 1
    max_batch_window_in_seconds = 0
  }

  retry_policy = {
    max_retry_attempts       = 5
    max_event_age_in_seconds = 300
    retry_strategy           = "ALL"
  }
}