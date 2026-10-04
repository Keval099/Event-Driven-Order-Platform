import json
import os
import time
import urllib.error
import urllib.request
import uuid

import boto3


API_URL = os.getenv(
    "API_BASE_URL",
    "https://hlxomiiwh3.execute-api.ap-south-1.amazonaws.com/dev/orders"
)

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE")

ORDERS_TABLE_NAME = os.getenv(
    "ORDERS_TABLE_NAME",
    "Orders"
)


def get_aws_session():
    if AWS_PROFILE:
        return boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION
        )

    return boto3.Session(
        region_name=AWS_REGION
    )


def post_order(body):
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        response_body = json.loads(
            error.read().decode("utf-8")
        )

        return error.code, response_body


def wait_for_order_status(
    table,
    order_id,
    expected_status,
    timeout_seconds=90
):
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        response = table.get_item(
            Key={
                "orderId": order_id
            }
        )

        item = response.get("Item")

        if item and item.get("status") == expected_status:
            return item

        time.sleep(3)

    return None


def test_create_order_end_to_end():
    customer_id = f"CUST-AUTO-E2E-{uuid.uuid4().hex[:8].upper()}"

    request_body = {
        "customerId": customer_id,
        "items": [
            {
                "productId": "PROD-E2E-001",
                "quantity": 1
            }
        ]
    }

    status_code, response = post_order(request_body)

    assert status_code == 202
    assert response["status"] == "PENDING"
    assert response["message"] == "Order accepted"

    order_id = response["orderId"]

    assert order_id.startswith("ORD-")

    session = get_aws_session()

    dynamodb = session.resource(
        "dynamodb",
        region_name=AWS_REGION
    )

    orders_table = dynamodb.Table(
        ORDERS_TABLE_NAME
    )

    item = wait_for_order_status(
        orders_table,
        order_id,
        "COMPLETED"
    )

    assert item is not None, (
        f"Order {order_id} did not reach COMPLETED "
        "within the timeout"
    )

    assert item["orderId"] == order_id
    assert item["customerId"] == customer_id
    assert item["status"] == "COMPLETED"