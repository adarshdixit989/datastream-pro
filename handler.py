"""Small Lambda entry point for scheduled analytics/archive jobs.
Keep the Lambda thin; heavy streaming work stays in Kafka consumers."""
import json
from datetime import datetime, timezone

def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"service":"datastream-pro-lambda","timestamp":datetime.now(timezone.utc).isoformat(),"trigger":event})
    }
