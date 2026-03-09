# Quick Start Guide - P11 Serverless API Gateway

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd /home/user/Portfolio-Project/projects-new/P11-serverless-api-gateway
make install
```

### 2. Run Tests
```bash
make test
```

### 3. Deploy to AWS
```bash
make deploy ENVIRONMENT=dev
```

### 4. Get Your API Endpoint
```bash
make endpoint ENVIRONMENT=dev
```

Output will be something like:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev
```

## Test the API

### Create an Item
```bash
ENDPOINT=$(make endpoint ENVIRONMENT=dev)
curl -X POST https://${ENDPOINT}/items \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Item",
    "description": "This is a test item",
    "price": 49.99
  }'
```

Response (save the `id`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My First Item",
  "description": "This is a test item",
  "price": 49.99,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Items
```bash
curl -X GET "https://${ENDPOINT}/items" \
  -H "Authorization: Bearer dev-key-12345"
```

### Get Specific Item
```bash
ITEM_ID="550e8400-e29b-41d4-a716-446655440000"
curl -X GET "https://${ENDPOINT}/items/${ITEM_ID}" \
  -H "Authorization: Bearer dev-key-12345"
```

### Update Item
```bash
ITEM_ID="550e8400-e29b-41d4-a716-446655440000"
curl -X PUT "https://${ENDPOINT}/items/${ITEM_ID}" \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Item Name",
    "price": 99.99
  }'
```

### Delete Item
```bash
ITEM_ID="550e8400-e29b-41d4-a716-446655440000"
curl -X DELETE "https://${ENDPOINT}/items/${ITEM_ID}" \
  -H "Authorization: Bearer dev-key-12345"
```

## File Structure

```
├── lambda_handlers/          # Your Lambda functions (production-ready)
│   ├── auth.py              # API Key validation
│   ├── base.py              # Shared utilities
│   ├── create.py            # POST /items
│   ├── read.py              # GET /items, GET /items/{id}
│   ├── update.py            # PUT /items/{id}
│   └── delete.py            # DELETE /items/{id}
├── tests/                    # Comprehensive test suite
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   ├── test_delete.py
│   ├── test_integration.py   # Full workflow tests
│   └── conftest.py
├── template.yaml            # AWS SAM infrastructure definition
├── Makefile                 # Build commands (deploy, test, etc.)
├── requirements.txt         # Python dependencies
└── IMPLEMENTATION.md        # Detailed documentation
```

## Make Commands

| Command | Purpose |
|---------|---------|
| `make install` | Install Python dependencies |
| `make test` | Run all tests |
| `make test-coverage` | Generate coverage report |
| `make lint` | Check code quality |
| `make format` | Format code |
| `make deploy ENVIRONMENT=dev` | Deploy to AWS |
| `make destroy ENVIRONMENT=dev` | Delete AWS stack |
| `make endpoint ENVIRONMENT=dev` | Show API endpoint |
| `make outputs ENVIRONMENT=dev` | Show CloudFormation outputs |
| `make clean` | Clean build artifacts |

## API Key

Default test API key: `dev-key-12345`

Change in `.env` or update `ALLOWED_API_KEYS` in AWS Secrets Manager after deployment.

## CloudWatch Logs

View logs for your deployment:

```bash
aws logs tail /aws/lambda/create-item-dev --follow
aws logs tail /aws/lambda/read-item-dev --follow
```

## X-Ray Tracing

View service map in AWS Console:
- Go to X-Ray → Service map
- Click on your Lambda functions to see trace details

## Common Issues

### 401 Unauthorized
Check the `Authorization` header contains the correct API key:
```bash
Authorization: Bearer dev-key-12345
```

### 404 Not Found
Verify the item ID is correct:
```bash
make endpoint ENVIRONMENT=dev
# Use the returned URL in your requests
```

### DynamoDB errors
Check the DynamoDB table exists:
```bash
aws dynamodb describe-table --table-name items-table-dev
```

## Next Steps

1. **Modify API Keys**: Update `ALLOWED_API_KEYS` in `.env`
2. **Scale for Production**: Change `Environment=dev` to `Environment=prod`
3. **Add More Fields**: Edit schemas in Lambda handlers
4. **Enable CORS**: Add CORS to `template.yaml` for web clients
5. **Add Caching**: Integrate with ElastiCache
6. **Monitor**: Set up CloudWatch alarms

## Cleanup

When done testing:

```bash
make destroy ENVIRONMENT=dev
```

This safely removes all AWS resources and associated costs.

## Support

- See `IMPLEMENTATION.md` for detailed documentation
- Check test files for usage examples
- Review `template.yaml` for infrastructure definition
- Read Lambda handler code for business logic

---

**You now have a production-ready serverless API!** 🚀
