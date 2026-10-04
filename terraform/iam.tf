resource "aws_iam_role" "order_api_lambda" {
  name        = "${var.project_name}-OrderApi-LambdaRole"
  description = "Allows Lambda functions to call AWS services on your behalf."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderApiLambda"
  }
}

resource "aws_iam_role" "order_processor_lambda" {
  name = "EventDrivenOrderPlatform-OrderProcessor-role-olgx3eq5"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderProcessorLambda"
  }
}

resource "aws_iam_role_policy_attachment" "order_api_logs" {
  role       = aws_iam_role.order_api_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "order_processor_logs" {
  role       = aws_iam_role.order_processor_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "order_api" {
  name = "OrderApiWriteOrders"
  role = aws_iam_role.order_api_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "WriteOrders"
        Effect = "Allow"

        Action = [
          "dynamodb:PutItem"
        ]

        Resource = aws_dynamodb_table.orders.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "order_api_publish_events" {
  name = "OrderApiPublishEvents"
  role = aws_iam_role.order_api_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid      = "PublishOrderEvents"
        Effect   = "Allow"
        Action   = ["events:PutEvents"]
        Resource = awscc_eventsv2_event_bus.orders.event_bus_arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "order_processor" {
  name = "OrderProcessorConsumeAndUpdate"
  role = aws_iam_role.order_processor_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ConsumeOrderQueue"
        Effect = "Allow"

        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]

        Resource = aws_sqs_queue.order_queue.arn
      },
      {
        Sid    = "StartOrderWorkflow"
        Effect = "Allow"

        Action = [
          "states:StartExecution"
        ]

        Resource = aws_sfn_state_machine.order_workflow.arn
      }
    ]
  })
}

resource "aws_iam_role" "order_workflow" {
  name = "${var.project_name}-OrderWorkflow-StepFunctionsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "states.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "StepFunctions"
  }
}

resource "aws_iam_role_policy" "order_workflow" {
  name = "${var.project_name}-OrderWorkflow-Policy"
  role = aws_iam_role.order_workflow.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "InvokeOrderWorker"
        Effect = "Allow"

        Action = [
          "lambda:InvokeFunction"
        ]

        Resource = aws_lambda_function.order_worker.arn
      },
      {
        Sid    = "UpdateOrders"
        Effect = "Allow"

        Action = [
          "dynamodb:UpdateItem"
        ]

        Resource = aws_dynamodb_table.orders.arn
      },
      {
        Sid    = "ManageProcessedEvents"
        Effect = "Allow"

        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]

        Resource = aws_dynamodb_table.processed_order_events.arn
      }
    ]
  })
}

resource "aws_iam_role" "order_worker_lambda" {
  name = "${var.project_name}-OrderWorker-LambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderWorkerLambda"
  }
}

resource "aws_iam_role_policy" "order_worker" {
  name = "${var.project_name}-OrderWorker-Policy"
  role = aws_iam_role.order_worker_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "UpdateOrders"
        Effect = "Allow"

        Action = [
          "dynamodb:UpdateItem"
        ]

        Resource = aws_dynamodb_table.orders.arn
      }
    ]
  })
}
