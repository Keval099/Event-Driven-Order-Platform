import json
import os
import time

import boto3


AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE")

EVENT_BUS_NAME = os.getenv(
    "EVENT_BUS_NAME",
    "EventDrivenOrderPlatform-Bus"
)

SQS_QUEUE_URL = os.getenv(
    "SQS_QUEUE_URL",
    "https://sqs.ap-south-1.amazonaws.com/825765413460/"
    "EventDrivenOrderPlatform-OrderQueue"
)


def get_aws_session():
    """
    Create an AWS session using the local AWS profile when provided.

    Local:
        AWS_PROFILE=ecr-lab

    GitHub Actions:
        AWS_PROFILE is not set, so boto3 uses the default credential
        chain populated by GitHub Actions OIDC.
    """
    if AWS_PROFILE:
        return boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION
        )

    return boto3.Session(
        region_name=AWS_REGION
    )


def get_event_bus_arn(eventbridge):
    response = eventbridge.list_event_buses(
        NamePrefix=EVENT_BUS_NAME
    )

    for bus in response.get("EventBuses", []):
        if bus["Name"] == EVENT_BUS_NAME:
            return bus["EventBusArn"]

    raise AssertionError(
        f"EventBridge V2 bus not found: {EVENT_BUS_NAME}"
    )


def get_visible_message_count(sqs):
    response = sqs.get_queue_attributes(
        QueueUrl=SQS_QUEUE_URL,
        AttributeNames=[
            "ApproximateNumberOfMessages"
        ]
    )

    return int(
        response["Attributes"]["ApproximateNumberOfMessages"]
    )


def test_non_order_created_event_is_filtered():
    session = get_aws_session()

    eventbridge = session.client(
        "eventbridgev2",
        region_name=AWS_REGION
    )

    sqs = session.client(
        "sqs",
        region_name=AWS_REGION
    )

    # Discover the current EventBridge V2 bus ARN.
    # This avoids hardcoding the generated bus identifier.
    event_bus_arn = get_event_bus_arn(eventbridge)

    print(
        "Using EventBridge V2 bus:",
        event_bus_arn
    )

    # The queue must be empty before this test.
    before_count = get_visible_message_count(sqs)

    assert before_count == 0, (
        "SQS queue is not empty before the filter test. "
        f"Visible messages: {before_count}"
    )

    # Publish an event that intentionally does NOT match
    # the deployed subscriber filter.
    #
    # Deployed filter:
    #   source      = event-driven-order-platform.orders
    #   detail-type = OrderCreated
    #
    # This test uses:
    #   detail-type = OrderCancelled
    #
    # Therefore the event should NOT be delivered to SQS.
    response = eventbridge.put_events(
        EventBusArn=event_bus_arn,
        Entries=[
            {
                "Source": "event-driven-order-platform.orders",
                "DetailType": "OrderCancelled",
                "Detail": json.dumps(
                    {
                        "orderId": "ORD-FILTER-TEST",
                        "customerId": "CUST-FILTER-TEST"
                    }
                )
            }
        ]
    )

    # EventBridge accepted the event.
    assert response["FailedEntryCount"] == 0

    assert response["Entries"][0]["SuccessCode"] == "PUBLISHED"

    # Give EventBridge V2 time to evaluate the subscriber filter.
    time.sleep(5)

    # The OrderCancelled event must not arrive in SQS.
    after_count = get_visible_message_count(sqs)

    assert after_count == 0, (
        "EventBridge filter failed: "
        "OrderCancelled event reached the SQS queue."
    )