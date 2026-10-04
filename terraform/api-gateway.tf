resource "aws_api_gateway_rest_api" "orders" {
  name        = "${var.project_name}-API"
  description = "REST API for the Event-Driven Order Platform"

  security_policy      = "SecurityPolicy_TLS13_1_2_2021_06"
  endpoint_access_mode = "STRICT"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "ApiGateway"
  }
}
resource "aws_api_gateway_resource" "orders" {
  rest_api_id = aws_api_gateway_rest_api.orders.id
  parent_id   = aws_api_gateway_rest_api.orders.root_resource_id
  path_part   = "orders"
}

resource "aws_api_gateway_method" "create_order" {
  rest_api_id   = aws_api_gateway_rest_api.orders.id
  resource_id   = aws_api_gateway_resource.orders.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "create_order" {
  rest_api_id = aws_api_gateway_rest_api.orders.id
  resource_id = aws_api_gateway_resource.orders.id
  http_method = aws_api_gateway_method.create_order.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.order_api.invoke_arn
  content_handling        = "CONVERT_TO_TEXT"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "cf482511-4743-5ba6-91d4-1bf68129be13"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_api.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.orders.execution_arn}/*/POST/orders"
}

resource "aws_api_gateway_deployment" "dev" {
  rest_api_id = aws_api_gateway_rest_api.orders.id
  description = "Initial orders API"

  depends_on = [
    aws_api_gateway_integration.create_order
  ]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "dev" {
  rest_api_id   = aws_api_gateway_rest_api.orders.id
  deployment_id = aws_api_gateway_deployment.dev.id
  stage_name    = var.environment
}