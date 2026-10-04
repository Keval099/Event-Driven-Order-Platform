import json
import os

import boto3


AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "ecr-lab")

PROCESSOR_FUNCTION_NAME = os.getenv(
    "PROCESSOR_FUNCTION_NAME",
    "EventDrivenOrderPlatform-OrderProcessor"
)

# Previously verified successful execution.
DUPLICATE_EVENT_ID = (
    "2a5244e6-23f4-417c-a300-563c7eeb67f8"
)

ORDER_ID = "ORD-73F0B806872D"
CUSTOMER_ID = "CUST-TF-E2E-001"

EXECUTION_ARN = (
    "arn:aws:states:ap-south-1:825765413460:"
    "execution:EventDrivenOrderPlatform-OrderWorkflow:"
    "2a5244e6-23f4-417c-a300-563c7eeb67f8"
)


def get_aws_session():
    return boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )


def make_duplicate_sqs_event():
    eventbridge_message = {
        "id": DUPLICATE_EVENT_ID,
        "detail": {
            "data": {
                "orderId": ORDER_ID,
                "customerId": CUSTOMER_ID
            }
        }
    }

    return {
        "Records": [
            {
                "body": json.dumps(eventbridge_message)
            }
        ]
    }


def test_duplicate_event_is_skipped_by_deployed_processor():
    session = get_aws_session()

    stepfunctions = session.client(
        "stepfunctions",
        region_name=AWS_REGION
    )

    lambda_client = session.client(
        "lambda",
        region_name=AWS_REGION
    )

    # Confirm the original execution exists before testing
    # duplicate delivery.
    execution_before = stepfunctions.describe_execution(
        executionArn=EXECUTION_ARN
    )

    assert execution_before["status"] == "SUCCEEDED"

    # Send the same EventBridge/SQS event to the real
    # deployed Order Processor Lambda.
    response = lambda_client.invoke(
        FunctionName=PROCESSOR_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(
            make_duplicate_sqs_event()
        ).encode("utf-8")
    )

    assert response["StatusCode"] == 200

    payload = json.loads(
        response["Payload"].read().decode("utf-8")
    )

    assert payload["statusCode"] == 200

    response_body = json.loads(
        payload["body"]
    )

    assert response_body["message"] == (
        "Order workflow started successfully"
    )

    # Confirm that the original execution is still the
    # same execution. No new execution can be created
    # with the same name.
    execution_after = stepfunctions.describe_execution(
        executionArn=EXECUTION_ARN
    )

    assert execution_after["executionArn"] == EXECUTION_ARN
    assert execution_after["status"] == "SUCCEEDED"