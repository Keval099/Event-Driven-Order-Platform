import json


def lambda_handler(event, context):
    print("Received SQS event:")
    print(json.dumps(event, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "SQS event received"
        })
    }