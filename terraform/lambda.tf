resource "aws_lambda_function" "order_api" {
  function_name = "${var.project_name}-OrderApi"

  role = aws_iam_role.order_api_lambda.arn

  runtime = "python3.14"
  handler = "functions.order_api.handler.lambda_handler"

  filename         = "${path.module}/build/order-api.zip"
  source_code_hash = filebase64sha256("${path.module}/build/order-api.zip")

  architectures = ["x86_64"]

  environment {
    variables = {
      ORDERS_TABLE_NAME = aws_dynamodb_table.orders.name
      EVENT_BUS_ARN     = awscc_eventsv2_event_bus.orders.event_bus_arn
    }
  }


  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderApi"
  }
}

resource "aws_lambda_function" "order_processor" {
  function_name = "${var.project_name}-OrderProcessor"

  role = aws_iam_role.order_processor_lambda.arn

  runtime = "python3.14"
  handler = "functions.order_processor.handler.lambda_handler"

  filename         = "${path.module}/build/order-processor.zip"
  source_code_hash = filebase64sha256("${path.module}/build/order-processor.zip")

  architectures = ["x86_64"]

  timeout     = 60
  memory_size = 128

  environment {
    variables = {
      ORDERS_TABLE_NAME           = aws_dynamodb_table.orders.name
      PROCESSED_EVENTS_TABLE_NAME = aws_dynamodb_table.processed_order_events.name
      STATE_MACHINE_ARN           = aws_sfn_state_machine.order_workflow.arn
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderProcessor"
  }
}

resource "aws_lambda_event_source_mapping" "order_processor_sqs" {
  event_source_arn = aws_sqs_queue.order_queue.arn
  function_name    = aws_lambda_function.order_processor.arn

  batch_size                         = 1
  maximum_batching_window_in_seconds = 0

  function_response_types = [
    "ReportBatchItemFailures"
  ]
}

resource "aws_lambda_function" "order_worker" {
  function_name = "${var.project_name}-OrderWorker"

  role = aws_iam_role.order_worker_lambda.arn

  runtime = "python3.13"
  handler = "functions.order_worker.handler.lambda_handler"

  filename         = "${path.module}/build/order-worker.zip"
  source_code_hash = filebase64sha256("${path.module}/build/order-worker.zip")

  architectures = ["x86_64"]

  timeout     = 60
  memory_size = 128

  environment {
    variables = {
      ORDERS_TABLE_NAME = aws_dynamodb_table.orders.name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderWorker"
  }
}