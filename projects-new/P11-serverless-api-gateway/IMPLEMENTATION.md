# P11 Serverless API Gateway - Implementation Guide

## Overview

This project implements a complete serverless REST API using AWS Lambda, API Gateway, and DynamoDB. It provides CRUD operations for managing items with full production-ready features including:

- Lambda function handlers for CREATE, READ, UPDATE, DELETE operations
- AWS SAM template for infrastructure as code
- Comprehensive unit and integration tests
- API key authentication
- X-Ray tracing support
- CloudWatch logging
- Least-privilege IAM roles

## Architecture

### Components

1. **API Gateway**: REST API endpoint for handling HTTP requests
2. **Lambda Functions**: 5 handler functions for different operations
   - `create.py`: POST /items - Create new items
   - `read.py`: GET /items and GET /items/{id} - Retrieve items
   - `update.py`: PUT /items/{id} - Update existing items
   - `delete.py`: DELETE /items/{id} - Delete items
   - `auth.py`: Custom authorizer for API Key validation

3. **DynamoDB**: NoSQL database for item storage
4. **CloudWatch**: Logs and metrics
5. **X-Ray**: Distributed tracing

### Request Flow

```
HTTP Request
    ↓
API Gateway
    ↓
API Key Authorizer (auth.py)
    ↓
Route to appropriate Lambda Handler
    ↓
DynamoDB Operation
    ↓
Format and return response via API Gateway
    ↓
HTTP Response
```

## Deployment

### Prerequisites

- AWS CLI configured with credentials
- AWS SAM CLI (optional, for local testing)
- Python 3.11+
- pip

### Steps

1. **Clone the repository**
   ```bash
   cd /home/user/Portfolio-Project/projects-new/P11-serverless-api-gateway
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Run tests locally**
   ```bash
   make test
   ```

4. **Deploy to AWS**
   ```bash
   make deploy ENVIRONMENT=dev
   ```

   Or with custom parameters:
   ```bash
   make deploy ENVIRONMENT=prod AWS_REGION=us-west-2 STACK_NAME=my-api
   ```

5. **Get the API endpoint**
   ```bash
   make endpoint ENVIRONMENT=dev
   ```

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Key variables:
- `ENVIRONMENT`: dev, staging, or prod
- `AWS_REGION`: AWS region (default: us-east-1)
- `ALLOWED_API_KEYS`: Comma-separated list of valid API keys

## API Usage

All API calls require the `Authorization` header with format: `Bearer <api-key>`

### Create Item

```bash
curl -X POST https://<api-gateway-url>/items \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Item Name",
    "description": "Item Description",
    "price": 99.99
  }'
```

Response (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Item Name",
  "description": "Item Description",
  "price": 99.99,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Items

```bash
curl -X GET "https://<api-gateway-url>/items?limit=10" \
  -H "Authorization: Bearer dev-key-12345"
```

Response (200 OK):
```json
{
  "items": [...],
  "count": 5,
  "last_key": null
}
```

### Get Specific Item

```bash
curl -X GET "https://<api-gateway-url>/items/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer dev-key-12345"
```

Response (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Item Name",
  ...
}
```

### Update Item

```bash
curl -X PUT "https://<api-gateway-url>/items/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "price": 49.99
  }'
```

Response (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Name",
  "price": 49.99,
  ...
}
```

### Delete Item

```bash
curl -X DELETE "https://<api-gateway-url>/items/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer dev-key-12345"
```

Response (204 No Content)

## Testing

### Unit Tests

Run all unit tests:
```bash
make test
```

Run specific test file:
```bash
pytest tests/test_create.py -v
```

Run with coverage report:
```bash
make test-coverage
```

### Integration Tests

Integration tests are included in `tests/test_integration.py` and test complete CRUD workflows:
- Full CRUD workflow (Create → Read → Update → Delete)
- Multiple concurrent-like operations
- Error scenarios and edge cases

### Test Files

- `tests/test_create.py` - CREATE operation tests
- `tests/test_read.py` - READ operation tests
- `tests/test_update.py` - UPDATE operation tests
- `tests/test_delete.py` - DELETE operation tests
- `tests/test_integration.py` - End-to-end workflow tests
- `tests/conftest.py` - Pytest fixtures and configuration

## Project Structure

```
P11-serverless-api-gateway/
├── lambda_handlers/          # Lambda function handlers
│   ├── __init__.py
│   ├── auth.py              # API Key authorization
│   ├── base.py              # Shared utilities
│   ├── create.py            # CREATE operation
│   ├── read.py              # READ operation
│   ├── update.py            # UPDATE operation
│   └── delete.py            # DELETE operation
├── tests/                    # Unit and integration tests
│   ├── conftest.py          # Pytest configuration
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   ├── test_delete.py
│   └── test_integration.py
├── events/                   # Sample Lambda events
│   ├── create_event.json
│   ├── read_event.json
│   ├── update_event.json
│   ├── delete_event.json
│   └── list_event.json
├── template.yaml            # SAM template
├── Makefile                 # Build automation
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example            # Environment variables example
└── IMPLEMENTATION.md       # This file
```

## Code Quality

### Linting

```bash
make lint
```

### Code Formatting

```bash
make format
```

### Full Check (lint + test + coverage)

```bash
make check
```

## Error Handling

All Lambda handlers return standard API Gateway formatted responses:

- **200 OK**: Successful GET/PUT operations
- **201 Created**: Successful POST operations
- **204 No Content**: Successful DELETE operations
- **400 Bad Request**: Invalid input or missing required fields
- **404 Not Found**: Item not found
- **500 Internal Server Error**: Unexpected server error

Error responses include a standardized error message:
```json
{
  "error": "Error description"
}
```

## Security Features

### API Key Authentication

All endpoints are protected with API Key authentication via a custom Lambda authorizer. API keys are validated against environment variables.

Valid test keys: `dev-key-12345`, `prod-key-67890`

### IAM Roles

The Lambda execution role has least-privilege permissions:
- DynamoDB: Only `GetItem`, `PutItem`, `UpdateItem`, `DeleteItem`, `Scan` operations on the items table
- CloudWatch Logs: Log group creation and writing
- X-Ray: Write-only access for tracing

### Data Validation

- Required fields are validated before database operations
- Type validation for numeric fields (price)
- String trimming to prevent whitespace-only entries
- Maximum list limit enforcement (1000 items)

## Monitoring and Logging

### CloudWatch Logs

Each Lambda function logs:
- Operation type (CREATE, READ, UPDATE, DELETE)
- Request ID
- API path and method
- Error details with stack traces

Log level can be controlled via `LOG_LEVEL` environment variable.

### X-Ray Tracing

X-Ray tracing is enabled for:
- API Gateway
- Lambda functions
- DynamoDB operations

Trace service map available in AWS X-Ray console.

## Cleanup

To delete the stack and all resources:

```bash
make destroy ENVIRONMENT=dev
```

This will:
1. Delete all Lambda functions
2. Delete the DynamoDB table
3. Delete the API Gateway
4. Delete the CloudWatch log groups
5. Remove IAM roles

## Cost Optimization

The SAM template uses different configurations for different environments:

- **Dev/Staging**: PAY_PER_REQUEST billing mode (no minimum cost)
- **Production**: PROVISIONED mode with 5 RCU/5 WCU (can be modified)
- **Production**: Point-in-time recovery enabled
- **Development**: 7-day log retention
- **Production**: 30-day log retention

Adjust in `template.yaml` for your cost requirements.

## Troubleshooting

### Lambda execution fails with "Table not found"

Ensure the `TABLE_NAME` environment variable matches the actual DynamoDB table name in your stack.

### 401 Unauthorized responses

Verify the API key in the `Authorization` header matches one of the allowed keys in the environment variables.

### DynamoDB capacity exceeded

If you're exceeding provisioned throughput on production:
1. Increase `ProvisionedThroughput` values in `template.yaml`
2. Consider switching to `PAY_PER_REQUEST` billing mode
3. Implement rate limiting in API Gateway

### Import errors in tests

Ensure the lambda_handlers directory is in Python path. The test conftest.py handles this automatically.

## Further Enhancements

Potential improvements for production:

1. **Caching**: Add ElastiCache for frequently accessed items
2. **Search**: Add global secondary indexes to DynamoDB
3. **Batch Operations**: Implement batch create/update endpoints
4. **Pagination**: Add pagination tokens for list operations
5. **Versioning**: Add API versioning support
6. **Rate Limiting**: Implement request throttling
7. **Database Encryption**: Enable DynamoDB encryption
8. **VPC**: Deploy Lambda functions in VPC for enhanced security
9. **CORS**: Add CORS support if needed for web clients
10. **Database Backups**: Enable automated backups and point-in-time recovery
