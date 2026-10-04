import json
import os
from unittest.mock import patch

from botocore.exceptions import ClientError


# The production module reads STATE_MACHINE_ARN during import.
os.environ["STATE_MACHINE_ARN"] = (
    "arn:aws:states:ap-south-1:123456789012:"
    "stateMachine:TestStateMachine"
)

from app.functions.order_processor.handler import lambda_handler


def make_sqs_event(
    event_id="event-001",
    order_id="ORD-001",
    customer_id="CUST-001"
):
    message = {
        "id": event_id,
        "detail": {
            "data": {
                "orderId": order_id,
                "customerId": customer_id
            }
        }
    }

    return {
        "Records": [
            {
                "body": json.dumps(message)
            }
        ]
    }


def test_valid_event_starts_step_functions_execution():
    event = make_sqs_event(
        event_id="event-001",
        order_id="ORD-001",
        customer_id="CUST-001"
    )

    with patch(
        "app.functions.order_processor.handler.stepfunctions.start_execution"
    ) as mock_start_execution:

        mock_start_execution.return_value = {
            "executionArn": (
                "arn:aws:states:ap-south-1:123456789012:"
                "execution:test-execution"
            )
        }

        response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    response_body = json.loads(response["body"])

    assert response_body["message"] == (
        "Order workflow started successfully"
    )

    mock_start_execution.assert_called_once()

    call_kwargs = mock_start_execution.call_args.kwargs

    assert call_kwargs["stateMachineArn"] == os.environ["STATE_MACHINE_ARN"]
    assert call_kwargs["name"] == "event-001"

    workflow_input = json.loads(call_kwargs["input"])

    assert workflow_input == {
        "eventId": "event-001",
        "orderId": "ORD-001",
        "customerId": "CUST-001"
    }


def test_duplicate_event_is_skipped():
    event = make_sqs_event(
        event_id="duplicate-event-001",
        order_id="ORD-002",
        customer_id="CUST-002"
    )

    duplicate_error = ClientError(
        {
            "Error": {
                "Code": "ExecutionAlreadyExists",
                "Message": "Execution already exists"
            }
        },
        "StartExecution"
    )

    with patch(
        "app.functions.order_processor.handler.stepfunctions.start_execution"
    ) as mock_start_execution:

        mock_start_execution.side_effect = duplicate_error

        response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    response_body = json.loads(response["body"])

    assert response_body["message"] == (
        "Order workflow started successfully"
    )

    mock_start_execution.assert_called_once()


def test_non_duplicate_step_functions_error_is_raised():
    event = make_sqs_event(
        event_id="event-error-001",
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
        "StartExecution"
    )

    with patch(
        "app.functions.order_processor.handler.stepfunctions.start_execution"
    ) as mock_start_execution:

        mock_start_execution.side_effect = error

        try:
            lambda_handler(event, None)
            assert False, "Expected ClientError to be raised"
        except ClientError as raised_error:
            assert (
                raised_error.response["Error"]["Code"]
                == "AccessDeniedException"
            )

        mock_start_execution.assert_called_once()


def test_multiple_sqs_records_start_multiple_workflows():
    event = {
        "Records": [
            {
                "body": json.dumps({
                    "id": "event-001",
                    "detail": {
                        "data": {
                            "orderId": "ORD-001",
                            "customerId": "CUST-001"
                        }
                    }
                })
            },
            {
                "body": json.dumps({
                    "id": "event-002",
                    "detail": {
                        "data": {
                            "orderId": "ORD-002",
                            "customerId": "CUST-002"
                        }
                    }
                })
            }
        ]
    }

    with patch(
        "app.functions.order_processor.handler.stepfunctions.start_execution"
    ) as mock_start_execution:

        mock_start_execution.side_effect = [
            {
                "executionArn": "arn:aws:states:test:execution-001"
            },
            {
                "executionArn": "arn:aws:states:test:execution-002"
            }
        ]

        response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    assert mock_start_execution.call_count == 2

    first_call = mock_start_execution.call_args_list[0].kwargs
    second_call = mock_start_execution.call_args_list[1].kwargs

    assert first_call["name"] == "event-001"
    assert second_call["name"] == "event-002"


def test_utf8_bom_is_removed_before_parsing():
    message = {
        "id": "event-bom-001",
        "detail": {
            "data": {
                "orderId": "ORD-BOM-001",
                "customerId": "CUST-BOM-001"
            }
        }
    }

    event = {
        "Records": [
            {
                "body": "\ufeff" + json.dumps(message)
            }
        ]
    }

    with patch(
        "app.functions.order_processor.handler.stepfunctions.start_execution"
    ) as mock_start_execution:

        mock_start_execution.return_value = {
            "executionArn": "arn:aws:states:test:bom-execution"
        }

        response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    mock_start_execution.assert_called_once()

    call_kwargs = mock_start_execution.call_args.kwargs

    assert call_kwargs["name"] == "event-bom-001"

    workflow_input = json.loads(call_kwargs["input"])

    assert workflow_input["orderId"] == "ORD-BOM-001"
    assert workflow_input["customerId"] == "CUST-BOM-001"