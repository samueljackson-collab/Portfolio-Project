"""API Gateway Lambda handlers with authentication."""
import json
import logging
import os
import boto3
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
sfn_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')

# Environment variables
STATE_MACHINE_ARN = os.environ.get('STATE_MACHINE_ARN')
METRICS_TABLE_NAME = os.environ.get('METRICS_TABLE_NAME')


def api_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create API Gateway response.

    Args:
        status_code: HTTP status code
        body: Response body

    Returns:
        API Gateway response format
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }


def start_processing_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API handler to start data processing workflow.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API response
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))

        # Extract user info from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims'].get('sub', 'anonymous')

        # Validate input
        if 'data' not in body:
            return api_response(400, {
                'error': 'Missing required field: data'
            })

        # Prepare input for Step Functions
        sfn_input = {
            'id': body.get('id', f"job-{datetime.utcnow().timestamp()}"),
            'data': body['data'],
            'user_id': user_id,
            'source': 'api',
            'timestamp': datetime.utcnow().isoformat()
        }

        # Start Step Functions execution
        response = sfn_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(sfn_input)
        )

        logger.info(f"Started execution: {response['executionArn']}")

        return api_response(202, {
            'message': 'Processing started',
            'execution_arn': response['executionArn'],
            'job_id': sfn_input['id']
        })

    except Exception as e:
        logger.error(f"Error starting processing: {str(e)}")
        return api_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })


def get_status_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get processing job status.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API response with job status
    """
    try:
        # Get execution ARN from path parameters
        execution_arn = event['pathParameters'].get('execution_arn')

        if not execution_arn:
            return api_response(400, {
                'error': 'Missing execution_arn parameter'
            })

        # Get execution details
        response = sfn_client.describe_execution(
            executionArn=execution_arn
        )

        return api_response(200, {
            'execution_arn': response['executionArn'],
            'status': response['status'],
            'start_date': response['startDate'].isoformat(),
            'stop_date': response.get('stopDate', '').isoformat() if response.get('stopDate') else None,
            'input': json.loads(response.get('input', '{}')),
            'output': json.loads(response.get('output', '{}')) if response.get('output') else None
        })

    except sfn_client.exceptions.ExecutionDoesNotExist:
        return api_response(404, {
            'error': 'Execution not found'
        })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return api_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })


def list_jobs_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    List recent processing jobs.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API response with job list
    """
    try:
        # Get query parameters
        params = event.get('queryStringParameters', {}) or {}
        limit = int(params.get('limit', 20))
        status_filter = params.get('status', 'RUNNING')

        # List executions
        response = sfn_client.list_executions(
            stateMachineArn=STATE_MACHINE_ARN,
            statusFilter=status_filter,
            maxResults=min(limit, 100)
        )

        executions = []
        for execution in response.get('executions', []):
            executions.append({
                'execution_arn': execution['executionArn'],
                'name': execution['name'],
                'status': execution['status'],
                'start_date': execution['startDate'].isoformat(),
                'stop_date': execution.get('stopDate', '').isoformat() if execution.get('stopDate') else None
            })

        return api_response(200, {
            'executions': executions,
            'count': len(executions)
        })

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return api_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })


def get_metrics_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get processing metrics.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API response with metrics
    """
    try:
        # Get metric ID from path parameters
        metric_id = event['pathParameters'].get('metric_id')

        if not metric_id:
            return api_response(400, {
                'error': 'Missing metric_id parameter'
            })

        # Query DynamoDB
        table = dynamodb.Table(METRICS_TABLE_NAME)
        response = table.get_item(
            Key={'metric_id': metric_id}
        )

        if 'Item' not in response:
            return api_response(404, {
                'error': 'Metric not found'
            })

        return api_response(200, response['Item'])

    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return api_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })


def authorizer_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Custom Lambda authorizer for API Gateway.

    Args:
        event: Authorizer event
        context: Lambda context

    Returns:
        IAM policy document
    """
    try:
        # Get token from Authorization header
        token = event.get('authorizationToken', '')

        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Validate token (implement actual validation logic)
        # For now, just check if token exists
        if not token:
            raise Exception('Unauthorized')

        # Generate IAM policy
        principal_id = 'user|123'  # Replace with actual user ID from token

        policy = {
            'principalId': principal_id,
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': event['methodArn']
                    }
                ]
            },
            'context': {
                'user_id': principal_id,
                'scope': 'read:write'
            }
        }

        return policy

    except Exception as e:
        logger.error(f"Authorization failed: {str(e)}")
        raise Exception('Unauthorized')
