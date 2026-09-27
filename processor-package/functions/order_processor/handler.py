import json
import os

import boto3
from botocore.exceptions import ClientError


ORDERS_TABLE_NAME = os.environ.get("ORDERS_TABLE_NAME", "Orders")

dynamodb = boto3.resource("dynamodb")
orders_table = dynamodb.Table(ORDERS_TABLE_NAME)


def lambda_handler(event, context):
    print("Received SQS event:")
    print(json.dumps(event, indent=2))

    for record in event["Records"]:
        sqs_body = json.loads(record["body"])

        detail = sqs_body["detail"]
        order_data = detail["data"]

        order_id = order_data["orderId"]
        customer_id = order_data["customerId"]

        print("Processing order:", order_id)
        print("Customer ID:", customer_id)

        # PENDING -> PROCESSING
        try:
            orders_table.update_item(
                Key={"orderId": order_id},
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
                    f"Order {order_id} is no longer PENDING. "
                    "It may already have been processed."
                )
                continue

            print("Failed to update order to PROCESSING")
            raise

        # Simulated order-processing work
        print("Processing order business logic...")

        # PROCESSING -> COMPLETED
        orders_table.update_item(
            Key={"orderId": order_id},
            UpdateExpression="SET #status = :completed",
            ConditionExpression="#status = :processing",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":processing": "PROCESSING",
                ":completed": "COMPLETED"
            }
        )

        print("Order status updated to COMPLETED")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Order event processed successfully"
        })
    }