import json


def lambda_handler(event, context):
    print("Received SQS event:")
    print(json.dumps(event, indent=2))

    for record in event["Records"]:
        sqs_body = json.loads(record["body"])

        print("EventBridge event:")
        print(json.dumps(sqs_body, indent=2))

        detail = sqs_body["detail"]
        order_data = detail["data"]

        order_id = order_data["orderId"]
        customer_id = order_data["customerId"]

        print("Order ID:", order_id)
        print("Customer ID:", customer_id)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Order event processed"
        })
    }