"""Lambda function for data transformation."""

import json
import os
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["METADATA_TABLE"])


def lambda_handler(event, context):
    """Transform data from raw bucket to processed format."""
    try:
        execution_id = event["execution_id"]
        s3_key = event["s3_key"]
        bucket = event["bucket"]

        # Update DynamoDB status
        table.update_item(
            Key={"execution_id": execution_id, "timestamp": event["timestamp"]},
            UpdateExpression="SET #status = :status, transform_start = :start",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "TRANSFORMING",
                ":start": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Download from S3
        response = s3.get_object(Bucket=bucket, Key=s3_key)
        raw_data = response["Body"].read().decode("utf-8")

        # Transform logic (example: CSV to JSON with enrichment)
        lines = raw_data.strip().split("\n")
        headers = lines[0].split(",")
        records = []

        for line in lines[1:]:
            values = line.split(",")
            record = dict(zip(headers, values))
            # Add enrichment
            record["processed_timestamp"] = datetime.now(timezone.utc).isoformat()
            record["processing_id"] = execution_id
            records.append(record)

        # Prepare output
        output_data = "\n".join([json.dumps(r) for r in records])
        output_key = s3_key.replace("raw/", "processed/").replace(".csv", ".jsonl")

        # Write to processed bucket
        processed_bucket = os.environ["PROCESSED_BUCKET"]
        s3.put_object(
            Bucket=processed_bucket,
            Key=output_key,
            Body=output_data.encode("utf-8"),
            ContentType="application/x-ndjson",
        )

        # Update DynamoDB
        table.update_item(
            Key={"execution_id": execution_id, "timestamp": event["timestamp"]},
            UpdateExpression="SET #status = :status, transform_end = :end, output_key = :key, record_count = :count",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "TRANSFORMED",
                ":end": datetime.now(timezone.utc).isoformat(),
                ":key": output_key,
                ":count": len(records),
            },
        )

        return {
            "statusCode": 200,
            "execution_id": execution_id,
            "output_key": output_key,
            "record_count": len(records),
        }

    except Exception as e:
        print(f"Transform error: {str(e)}")
        # Update DynamoDB with error
        if "execution_id" in event:
            table.update_item(
                Key={
                    "execution_id": event["execution_id"],
                    "timestamp": event["timestamp"],
                },
                UpdateExpression="SET #status = :status, error_message = :error",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": "FAILED", ":error": str(e)},
            )
        raise
