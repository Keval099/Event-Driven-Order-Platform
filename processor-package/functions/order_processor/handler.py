import json
import os

import boto3
from botocore.exceptions import ClientError


ORDERS_TABLE_NAME = os.environ.get("ORDERS_TABLE_NAME", "Orders")
PROCESSED_EVENTS_TABLE_NAME = os.environ.get(
    "PROCESSED_EVENTS_TABLE_NAME",
    "ProcessedOrderEvents"
)

dynamodb = boto3.resource("dynamodb")

orders_table = dynamodb.Table(ORDERS_TABLE_NAME)
processed_events_table = dynamodb.Table(PROCESSED_EVENTS_TABLE_NAME)


def lambda_handler(event, context):
    print("Received SQS event:")
    print(json.dumps(event, indent=2))

    for record in event["Records"]:
        body = record["body"]

        if body.startswith("\ufeff"):
            body = body.removeprefix("\ufeff")
        elif body.startswith("ï»¿"):
            body = body.removeprefix("ï»¿")

        sqs_body = json.loads(body)

        detail = sqs_body["detail"]
        order_data = detail["data"]

        event_id = sqs_body["id"]

        order_id = order_data["orderId"]
        customer_id = order_data["customerId"]

        print("Processing order:", order_id)
        print("Customer ID:", customer_id)
        print("Event ID:", event_id)

        # ---------------------------------------------------------
        # IDEMPOTENCY CHECK / CLAIM
        # ---------------------------------------------------------
        try:
            processed_events_table.put_item(
                Item={
                    "eventId": event_id,
                    "orderId": order_id,
                    "status": "PROCESSING"
                },
                ConditionExpression="attribute_not_exists(eventId)"
            )

            print(f"Event {event_id} claimed for processing")

        except ClientError as error:
            error_code = error.response["Error"]["Code"]

            if error_code == "ConditionalCheckFailedException":
                print(
                    f"Duplicate event detected: {event_id}. "
                    "Skipping duplicate."
                )
                continue

            print("Failed to claim event for processing")
            raise

        # ---------------------------------------------------------
        # PENDING -> PROCESSING
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # SIMULATED ORDER-PROCESSING WORK
        # ---------------------------------------------------------
        print("Processing order business logic...")

        # ---------------------------------------------------------
        # PROCESSING -> COMPLETED
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # MARK EVENT AS COMPLETED
        # ---------------------------------------------------------
        processed_events_table.update_item(
            Key={"eventId": event_id},
            UpdateExpression="SET #status = :completed",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":completed": "COMPLETED"
            }
        )

        print(f"Event {event_id} marked as COMPLETED")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Order event processed successfully"
        })
    }