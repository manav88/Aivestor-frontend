import json
import boto3
import requests

POLYGON_API_KEY = "XX"

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters", {})
        ticker = params.get("ticker")

        if not ticker:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing ticker"})
            }

        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/2023-11-01/2024-04-30?adjusted=true&sort=asc&limit=1000&apiKey={POLYGON_API_KEY}"
        res = requests.get(url)

        if res.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Polygon API failed"})
            }

        data = res.json()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "dates": [item["t"] for item in data["results"]],
                "prices": [item["c"] for item in data["results"]]
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
