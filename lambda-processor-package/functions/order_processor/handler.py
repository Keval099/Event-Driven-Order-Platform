import json
import os

import boto3
from botocore.exceptions import ClientError


STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

stepfunctions = boto3.client("stepfunctions")


def lambda_handler(event, context):
    print("Received SQS event:")
    print(json.dumps(event, indent=2))

    for record in event["Records"]:
        body = record["body"]

        # Handle possible UTF-8 BOMs from manually-created test messages.
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

        print("Received OrderCreated event")
        print("Event ID:", event_id)
        print("Order ID:", order_id)
        print("Customer ID:", customer_id)

        workflow_input = {
            "eventId": event_id,
            "orderId": order_id,
            "customerId": customer_id
        }

        try:
            response = stepfunctions.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                name=event_id,
                input=json.dumps(workflow_input)
            )

            print("Step Functions execution started")
            print("Execution ARN:", response["executionArn"])

        except ClientError as error:
            error_code = error.response["Error"]["Code"]

            if error_code == "ExecutionAlreadyExists":
                print(
                    f"Step Functions execution already exists for event "
                    f"{event_id}. Treating event as duplicate."
                )
                continue

            print("Failed to start Step Functions execution")
            raise

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Order workflow started successfully"
        })
    }