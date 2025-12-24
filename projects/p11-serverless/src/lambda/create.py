#!/usr/bin/env python3
"""Lambda function to create items."""
import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'items-table')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """Create a new item."""
    try:
        body = json.loads(event['body'])
        item = {
            'id': str(datetime.now().timestamp()),
            'name': body['name'],
            'description': body.get('description', ''),
            'created_at': datetime.now().isoformat()
        }

        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(item)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
