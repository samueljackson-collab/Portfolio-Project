"""
Tests for API Gateway Lambda handlers.

Tests cover:
- API response formatting
- Start processing endpoint
- Get status endpoint
- List jobs endpoint
- Custom authorizer
"""

import pytest
import json
import os
from unittest.mock import MagicMock, patch
import sys

# Add functions directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions'))

from api_handlers import (
    api_response,
    start_processing_handler,
    get_status_handler,
    list_jobs_handler,
    get_metrics_handler,
    authorizer_handler,
)


class TestApiResponse:
    """Test API response helper."""

    def test_api_response_format(self):
        """Test API response has correct format."""
        response = api_response(200, {'message': 'success'})

        assert response['statusCode'] == 200
        assert 'headers' in response
        assert 'body' in response

    def test_api_response_headers(self):
        """Test API response has CORS headers."""
        response = api_response(200, {})

        headers = response['headers']
        assert headers['Content-Type'] == 'application/json'
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Headers' in headers
        assert 'Access-Control-Allow-Methods' in headers

    def test_api_response_body_serialization(self):
        """Test API response body is JSON serialized."""
        data = {'key': 'value', 'number': 123}
        response = api_response(200, data)

        body = json.loads(response['body'])
        assert body['key'] == 'value'
        assert body['number'] == 123

    def test_api_response_error_codes(self):
        """Test API response with different status codes."""
        for code in [200, 201, 400, 401, 404, 500]:
            response = api_response(code, {'error': 'test'})
            assert response['statusCode'] == code


class TestStartProcessingHandler:
    """Test start_processing_handler."""

    @patch('api_handlers.sfn_client')
    def test_start_processing_success(self, mock_sfn):
        """Test successful processing start."""
        mock_sfn.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456:execution:test:123'
        }

        event = {
            'body': json.dumps({'data': {'test': 'data'}}),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = start_processing_handler(event, None)

        assert response['statusCode'] == 202
        body = json.loads(response['body'])
        assert 'execution_arn' in body
        assert body['message'] == 'Processing started'

    @patch('api_handlers.sfn_client')
    def test_start_processing_missing_data(self, mock_sfn):
        """Test error when data field is missing."""
        event = {
            'body': json.dumps({'other': 'field'}),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = start_processing_handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Missing required field' in body['error']

    @patch('api_handlers.sfn_client')
    def test_start_processing_sfn_error(self, mock_sfn):
        """Test error handling when Step Functions fails."""
        mock_sfn.start_execution.side_effect = Exception('SFN Error')

        event = {
            'body': json.dumps({'data': {'test': 'data'}}),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = start_processing_handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body


class TestGetStatusHandler:
    """Test get_status_handler."""

    @patch('api_handlers.sfn_client')
    def test_get_status_success(self, mock_sfn):
        """Test successful status retrieval."""
        from datetime import datetime
        mock_sfn.describe_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456:execution:test:123',
            'status': 'SUCCEEDED',
            'startDate': datetime(2024, 1, 15, 10, 30),
            'stopDate': datetime(2024, 1, 15, 10, 31),
            'input': '{"data": "test"}',
            'output': '{"result": "success"}'
        }

        event = {
            'pathParameters': {
                'execution_arn': 'arn:aws:states:us-east-1:123456:execution:test:123'
            }
        }

        response = get_status_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'SUCCEEDED'

    @patch('api_handlers.sfn_client')
    def test_get_status_missing_param(self, mock_sfn):
        """Test error when execution_arn is missing."""
        event = {'pathParameters': {}}

        response = get_status_handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Missing execution_arn' in body['error']

    @patch('api_handlers.sfn_client')
    def test_get_status_not_found(self, mock_sfn):
        """Test error when execution doesn't exist."""
        mock_sfn.describe_execution.side_effect = \
            mock_sfn.exceptions.ExecutionDoesNotExist({}, 'describe_execution')

        event = {
            'pathParameters': {'execution_arn': 'invalid-arn'}
        }

        response = get_status_handler(event, None)

        assert response['statusCode'] == 404


class TestListJobsHandler:
    """Test list_jobs_handler."""

    @patch('api_handlers.sfn_client')
    def test_list_jobs_success(self, mock_sfn):
        """Test successful job listing."""
        from datetime import datetime
        mock_sfn.list_executions.return_value = {
            'executions': [
                {
                    'executionArn': 'arn:1',
                    'name': 'execution-1',
                    'status': 'RUNNING',
                    'startDate': datetime(2024, 1, 15, 10, 30)
                },
                {
                    'executionArn': 'arn:2',
                    'name': 'execution-2',
                    'status': 'RUNNING',
                    'startDate': datetime(2024, 1, 15, 10, 31)
                }
            ]
        }

        event = {'queryStringParameters': None}

        response = list_jobs_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 2
        assert len(body['executions']) == 2

    @patch('api_handlers.sfn_client')
    def test_list_jobs_with_filters(self, mock_sfn):
        """Test job listing with query parameters."""
        mock_sfn.list_executions.return_value = {'executions': []}

        event = {
            'queryStringParameters': {
                'limit': '5',
                'status': 'SUCCEEDED'
            }
        }

        response = list_jobs_handler(event, None)

        assert response['statusCode'] == 200
        mock_sfn.list_executions.assert_called_once()
        call_args = mock_sfn.list_executions.call_args
        assert call_args.kwargs['statusFilter'] == 'SUCCEEDED'
        assert call_args.kwargs['maxResults'] == 5


class TestGetMetricsHandler:
    """Test get_metrics_handler."""

    @patch('api_handlers.dynamodb')
    def test_get_metrics_success(self, mock_dynamodb):
        """Test successful metrics retrieval."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            'Item': {
                'metric_id': 'test-metric',
                'value': 100,
                'timestamp': '2024-01-15T10:30:00Z'
            }
        }
        mock_dynamodb.Table.return_value = mock_table

        event = {
            'pathParameters': {'metric_id': 'test-metric'}
        }

        response = get_metrics_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['metric_id'] == 'test-metric'

    @patch('api_handlers.dynamodb')
    def test_get_metrics_not_found(self, mock_dynamodb):
        """Test error when metric doesn't exist."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}  # No 'Item' key
        mock_dynamodb.Table.return_value = mock_table

        event = {
            'pathParameters': {'metric_id': 'nonexistent'}
        }

        response = get_metrics_handler(event, None)

        assert response['statusCode'] == 404


class TestAuthorizerHandler:
    """Test authorizer_handler."""

    def test_authorizer_with_valid_token(self):
        """Test authorizer with valid Bearer token."""
        event = {
            'authorizationToken': 'Bearer valid-token-123',
            'methodArn': 'arn:aws:execute-api:us-east-1:123456:api/GET/resource'
        }

        response = authorizer_handler(event, None)

        assert response['principalId'] is not None
        assert 'policyDocument' in response
        assert response['policyDocument']['Statement'][0]['Effect'] == 'Allow'

    def test_authorizer_without_bearer_prefix(self):
        """Test authorizer with token without Bearer prefix."""
        event = {
            'authorizationToken': 'direct-token-123',
            'methodArn': 'arn:aws:execute-api:us-east-1:123456:api/GET/resource'
        }

        response = authorizer_handler(event, None)

        assert response['principalId'] is not None
        assert response['policyDocument']['Statement'][0]['Effect'] == 'Allow'

    def test_authorizer_missing_token(self):
        """Test authorizer with missing token."""
        event = {
            'authorizationToken': '',
            'methodArn': 'arn:aws:execute-api:us-east-1:123456:api/GET/resource'
        }

        with pytest.raises(Exception, match='Unauthorized'):
            authorizer_handler(event, None)

    def test_authorizer_bearer_only(self):
        """Test authorizer with only Bearer prefix."""
        event = {
            'authorizationToken': 'Bearer ',
            'methodArn': 'arn:aws:execute-api:us-east-1:123456:api/GET/resource'
        }

        with pytest.raises(Exception, match='Unauthorized'):
            authorizer_handler(event, None)
