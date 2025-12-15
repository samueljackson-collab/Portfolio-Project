"""Lambda function for final output delivery."""
import json
import os
import boto3
from datetime import datetime, timezone

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['METADATA_TABLE'])
sns = boto3.client('sns')

def lambda_handler(event, context):
    """Finalize output and send notifications."""
    try:
        execution_id = event['execution_id']
        output_key = event['output_key']
        record_count = event['record_count']

        # Update DynamoDB with completion
        table.update_item(
            Key={'execution_id': execution_id, 'timestamp': event['timestamp']},
            UpdateExpression='SET #status = :status, completion_time = :time',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'COMPLETED',
                ':time': datetime.now(timezone.utc).isoformat()
            }
        )

        # Optional: Send SNS notification
        # sns.publish(
        #     TopicArn=os.environ.get('SNS_TOPIC_ARN'),
        #     Subject=f'ETL Completed: {execution_id}',
        #     Message=json.dumps({
        #         'execution_id': execution_id,
        #         'output_key': output_key,
        #         'record_count': record_count,
        #         'status': 'SUCCESS'
        #     })
        # )

        return {
            'statusCode': 200,
            'execution_id': execution_id,
            'status': 'COMPLETED',
            'output_key': output_key,
            'record_count': record_count
        }

    except Exception as e:
        print(f"Output error: {str(e)}")
        # Update DynamoDB with error
        if 'execution_id' in event:
            table.update_item(
                Key={'execution_id': event['execution_id'], 'timestamp': event['timestamp']},
                UpdateExpression='SET #status = :status, error_message = :error',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'FAILED', ':error': str(e)}
            )
        raise
