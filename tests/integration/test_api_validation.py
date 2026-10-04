import json
import os
import urllib.error
import urllib.request


API_URL = os.getenv(
    "API_BASE_URL",
    "https://hlxomiiwh3.execute-api.ap-south-1.amazonaws.com/dev/orders"
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


def test_missing_customer_id_returns_400():
    status_code, response = post_order({
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 1
            }
        ]
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"


def test_empty_customer_id_returns_400():
    status_code, response = post_order({
        "customerId": "",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 1
            }
        ]
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"


def test_empty_items_returns_400():
    status_code, response = post_order({
        "customerId": "CUST-INTEGRATION-001",
        "items": []
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"


def test_missing_product_id_returns_400():
    status_code, response = post_order({
        "customerId": "CUST-INTEGRATION-002",
        "items": [
            {
                "quantity": 1
            }
        ]
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"


def test_zero_quantity_returns_400():
    status_code, response = post_order({
        "customerId": "CUST-INTEGRATION-003",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 0
            }
        ]
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"


def test_negative_quantity_returns_400():
    status_code, response = post_order({
        "customerId": "CUST-INTEGRATION-004",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": -1
            }
        ]
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"


def test_non_integer_quantity_returns_400():
    status_code, response = post_order({
        "customerId": "CUST-INTEGRATION-005",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 1.5
            }
        ]
    })

    assert status_code == 400
    assert response["error"] == "ValidationError"