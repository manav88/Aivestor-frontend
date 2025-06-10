import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("AivestorDecisions")

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters", {})
        ticker = params.get("ticker")

        if not ticker:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing ticker"})
            }

        response = table.query(
            KeyConditionExpression=Key("ticker").eq(ticker),
            ScanIndexForward=False  # newest first
        )

        return {
            "statusCode": 200,
            "body": json.dumps(response["Items"])
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }