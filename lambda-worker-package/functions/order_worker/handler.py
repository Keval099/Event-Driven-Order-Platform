import json
import os

import boto3
from botocore.exceptions import ClientError


ORDERS_TABLE_NAME = os.environ.get("ORDERS_TABLE_NAME", "Orders")

dynamodb = boto3.resource("dynamodb")
orders_table = dynamodb.Table(ORDERS_TABLE_NAME)


def lambda_handler(event, context):
    print("Order Worker received:")
    print(json.dumps(event, indent=2))

    order_id = event["orderId"]
    customer_id = event["customerId"]

    print("Processing order:", order_id)
    print("Customer ID:", customer_id)

    # PENDING -> PROCESSING
    try:
        orders_table.update_item(
            Key={
                "orderId": order_id
            },
            UpdateExpression="SET #status = :processing",
            ConditionExpression="#status = :pending",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":pending": "PENDING",
                ":processing": "PROCESSING"
            }
        )

        print("Order status updated to PROCESSING")

    except ClientError as error:
        error_code = error.response["Error"]["Code"]

        if error_code == "ConditionalCheckFailedException":
            print(
                f"Order {order_id} is not PENDING. "
                "It may already be processing or completed."
            )
            raise

        print("Failed to update order to PROCESSING")
        raise

    # Simulated business processing
    print("Processing order business logic...")

    return {
        "orderId": order_id,
        "customerId": customer_id,
        "status": "PROCESSING"
    }