import json
from unittest.mock import patch

from botocore.exceptions import ClientError

from app.functions.order_worker.handler import lambda_handler


def make_event(
    order_id="ORD-001",
    customer_id="CUST-001"
):
    return {
        "orderId": order_id,
        "customerId": customer_id
    }


def test_valid_order_updates_to_processing():
    event = make_event(
        order_id="ORD-001",
        customer_id="CUST-001"
    )

    with patch(
        "app.functions.order_worker.handler.orders_table.update_item"
    ) as mock_update_item:

        response = lambda_handler(event, None)

    assert response == {
        "orderId": "ORD-001",
        "customerId": "CUST-001",
        "status": "PROCESSING"
    }

    mock_update_item.assert_called_once()

    call_kwargs = mock_update_item.call_args.kwargs

    assert call_kwargs["Key"] == {
        "orderId": "ORD-001"
    }

    assert call_kwargs["UpdateExpression"] == (
        "SET #status = :processing"
    )

    assert call_kwargs["ConditionExpression"] == (
        "#status = :pending"
    )

    assert call_kwargs["ExpressionAttributeValues"] == {
        ":pending": "PENDING",
        ":processing": "PROCESSING"
    }


def test_conditional_check_failure_is_raised():
    event = make_event(
        order_id="ORD-002",
        customer_id="CUST-002"
    )

    error = ClientError(
        {
            "Error": {
                "Code": "ConditionalCheckFailedException",
                "Message": "The conditional request failed"
            }
        },
        "UpdateItem"
    )

    with patch(
        "app.functions.order_worker.handler.orders_table.update_item"
    ) as mock_update_item:

        mock_update_item.side_effect = error

        try:
            lambda_handler(event, None)
            assert False, "Expected ClientError to be raised"
        except ClientError as raised_error:
            assert (
                raised_error.response["Error"]["Code"]
                == "ConditionalCheckFailedException"
            )

        mock_update_item.assert_called_once()


def test_other_dynamodb_error_is_raised():
    event = make_event(
        order_id="ORD-003",
        customer_id="CUST-003"
    )

    error = ClientError(
        {
            "Error": {
                "Code": "AccessDeniedException",
                "Message": "Not authorized"
            }
        },
        "UpdateItem"
    )

    with patch(
        "app.functions.order_worker.handler.orders_table.update_item"
    ) as mock_update_item:

        mock_update_item.side_effect = error

        try:
            lambda_handler(event, None)
            assert False, "Expected ClientError to be raised"
        except ClientError as raised_error:
            assert (
                raised_error.response["Error"]["Code"]
                == "AccessDeniedException"
            )

        mock_update_item.assert_called_once()


def test_worker_preserves_order_and_customer_ids():
    event = make_event(
        order_id="ORD-ABC123",
        customer_id="CUST-XYZ789"
    )

    with patch(
        "app.functions.order_worker.handler.orders_table.update_item"
    ):

        response = lambda_handler(event, None)

    assert response["orderId"] == "ORD-ABC123"
    assert response["customerId"] == "CUST-XYZ789"
    assert response["status"] == "PROCESSING"