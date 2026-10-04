import json
from unittest.mock import patch

from app.functions.order_api.handler import lambda_handler


def make_event(body):
    return {
        "body": json.dumps(body)
    }


def test_valid_order_returns_202():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 2
            }
        ]
    }

    with patch(
        "app.functions.order_api.handler.orders_table.put_item"
    ) as mock_put_item, patch(
        "app.functions.order_api.handler.events_client.put_events"
    ) as mock_put_events:

        mock_put_events.return_value = {
            "FailedEntryCount": 0
        }

        response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 202

    response_body = json.loads(response["body"])

    assert response_body["status"] == "PENDING"
    assert response_body["message"] == "Order accepted"
    assert response_body["orderId"].startswith("ORD-")

    mock_put_item.assert_called_once()
    mock_put_events.assert_called_once()


def test_missing_customer_id_returns_400():
    body = {
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 1
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400

    response_body = json.loads(response["body"])

    assert response_body["error"] == "ValidationError"
    assert response_body["message"] == "customerId is required"


def test_empty_customer_id_returns_400():
    body = {
        "customerId": "   ",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 1
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_missing_items_returns_400():
    body = {
        "customerId": "CUST-001"
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_empty_items_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": []
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_item_must_be_object():
    body = {
        "customerId": "CUST-001",
        "items": ["invalid-item"]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_missing_product_id_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "quantity": 1
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_empty_product_id_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "productId": "   ",
                "quantity": 1
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_zero_quantity_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 0
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_negative_quantity_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": -1
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_non_integer_quantity_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 1.5
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400


def test_boolean_quantity_returns_400():
    body = {
        "customerId": "CUST-001",
        "items": [
            {
                "productId": "PROD-001",
                "quantity": True
            }
        ]
    }

    response = lambda_handler(make_event(body), None)

    assert response["statusCode"] == 400