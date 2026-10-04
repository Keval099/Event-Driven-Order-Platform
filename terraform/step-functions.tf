resource "aws_sfn_state_machine" "order_workflow" {
  name     = "${var.project_name}-OrderWorkflow"
  role_arn = aws_iam_role.order_workflow.arn
  type     = "STANDARD"

  definition = jsonencode({
    Comment = "Order processing workflow with event idempotency"

    StartAt = "ClaimEvent"

    States = {
      ClaimEvent = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:putItem"

        Parameters = {
          TableName = aws_dynamodb_table.processed_order_events.name

          Item = {
            eventId = {
              "S.$" = "$.eventId"
            }

            orderId = {
              "S.$" = "$.orderId"
            }

            status = {
              "S" = "PROCESSING"
            }
          }

          ConditionExpression = "attribute_not_exists(eventId)"
        }

        Catch = [
          {
            ErrorEquals = [
              "DynamoDB.ConditionalCheckFailedException"
            ]

            Next = "DuplicateEvent"
          }
        ]

        ResultPath = null

        Next = "ProcessOrder"
      }

      DuplicateEvent = {
        Type = "Pass"

        Result = {
          status = "DUPLICATE"
        }

        End = true
      }

      ProcessOrder = {
        Type     = "Task"
        Resource = aws_lambda_function.order_worker.arn

        ResultPath = "$.workerResult"

        Next = "CompleteOrder"
      }

      CompleteOrder = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:updateItem"

        Parameters = {
          TableName = aws_dynamodb_table.orders.name

          Key = {
            orderId = {
              "S.$" = "$.orderId"
            }
          }

          UpdateExpression = "SET #status = :completed"

          ConditionExpression = "#status = :processing"

          ExpressionAttributeNames = {
            "#status" = "status"
          }

          ExpressionAttributeValues = {
            ":completed" = {
              "S" = "COMPLETED"
            }

            ":processing" = {
              "S" = "PROCESSING"
            }
          }
        }

        ResultPath = null

        Next = "MarkEventCompleted"
      }

      MarkEventCompleted = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:updateItem"

        Parameters = {
          TableName = aws_dynamodb_table.processed_order_events.name

          Key = {
            eventId = {
              "S.$" = "$.eventId"
            }
          }

          UpdateExpression = "SET #status = :completed"

          ExpressionAttributeNames = {
            "#status" = "status"
          }

          ExpressionAttributeValues = {
            ":completed" = {
              "S" = "COMPLETED"
            }
          }
        }

        ResultPath = null

        End = true
      }
    }
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "OrderWorkflow"
  }
}