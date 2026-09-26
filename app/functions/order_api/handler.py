import json
import uuid
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError
import os


def lambda_handler(event, context):
    print("Received event:")
    print(event)

    body = json.loads(event["body"])

    print("Parsed request body:")
    print(body)

    customer_id = body.get("customerId")
    items = body.get("items")

    # Validate customerId
    if not isinstance(customer_id, str) or not customer_id.strip():
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "ValidationError",
                "message": "customerId is required"
            })
        }

    # Validate items
    if not isinstance(items, list) or len(items) == 0:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "ValidationError",
                "message": "items must contain at least one item"
            })
        }

    # Validate each item
    for item in items:
        if not isinstance(item, dict):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "ValidationError",
                    "message": "each item must be an object"
                })
            }

        product_id = item.get("productId")
        quantity = item.get("quantity")

        if not isinstance(product_id, str) or not product_id.strip():
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "ValidationError",
                    "message": "productId is required"
                })
            }

        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "ValidationError",
                    "message": "quantity must be an integer greater than 0"
                })
            }

    order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"

    print("Generated order ID:")
    print(order_id)

    created_at = datetime.now(timezone.utc).isoformat()
    order = {
        "orderId": order_id,
        "customerId": customer_id,
        "items": items,
        "status": "PENDING",
        "createdAt": created_at
    }

    print("Created order:")
    print(json.dumps(order, indent=4))

    try:
        orders_table.put_item(Item=order)
        print("Order saved to DynamoDB")

    except ClientError as error:
        print("DynamoDB error:")
        print(error)

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "InternalServerError",
                "message": "Unable to save order"
            })
        }

    return {
        "statusCode": 202,
        "body": json.dumps({
            "orderId": order_id,
            "status": "PENDING",
            "message": "Order accepted"
        })
    }


AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
ORDERS_TABLE_NAME = os.getenv("ORDERS_TABLE_NAME", "Orders")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

orders_table = dynamodb.Table(ORDERS_TABLE_NAME)
print("Connected to DynamoDB table:", orders_table.name)

if __name__ == "__main__":
    test_event = {
        "body": '{"customerId":"CUST-001","items":[{"productId":"PROD-001","quantity":2}]}'
    }

    result = lambda_handler(test_event, None)

    print("Lambda response:")
    print(result)
