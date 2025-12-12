# P11: API Gateway & Serverless

Build a production-ready REST API using AWS Lambda, API Gateway, and DynamoDB. This project implements a complete serverless CRUD API with authentication, comprehensive testing, and infrastructure as code.

## What's Implemented

### Core Features
- ✅ **Lambda Functions**: Python-based handlers for CREATE, READ, UPDATE, DELETE operations
- ✅ **API Gateway**: REST API with HTTP methods and path parameters
- ✅ **DynamoDB**: NoSQL database with proper key schema
- ✅ **Authentication**: API Key validation via custom Lambda authorizer
- ✅ **Error Handling**: Comprehensive error responses with proper status codes
- ✅ **Logging**: CloudWatch integration with structured logging
- ✅ **Tracing**: AWS X-Ray for distributed tracing
- ✅ **Testing**: 22 unit and integration tests with moto mocking
- ✅ **Infrastructure as Code**: AWS SAM template with environment-specific configs
- ✅ **Deployment Automation**: Makefile with deploy, test, and cleanup targets
- ✅ **Documentation**: Complete guides including quickstart, deployment, and implementation details

### Project Structure
```
P11-serverless-api-gateway/
├── lambda_handlers/          # Production Lambda functions (7 handlers)
│   ├── base.py              # Shared utilities and helpers
│   ├── auth.py              # API Key authorization
│   ├── create.py            # POST /items
│   ├── read.py              # GET /items, GET /items/{id}
│   ├── update.py            # PUT /items/{id}
│   └── delete.py            # DELETE /items/{id}
├── tests/                    # Comprehensive test suite (22 tests)
│   ├── test_create.py       # CREATE operation tests
│   ├── test_read.py         # READ operation tests
│   ├── test_update.py       # UPDATE operation tests
│   ├── test_delete.py       # DELETE operation tests
│   ├── test_integration.py  # End-to-end workflow tests
│   └── conftest.py          # Pytest fixtures
├── events/                   # Sample Lambda test events
├── template.yaml            # AWS SAM template (production-ready)
├── Makefile                 # Build and deployment automation
├── requirements.txt         # Python dependencies
└── Documentation files
    ├── QUICKSTART.md        # 5-minute setup guide
    ├── DEPLOYMENT.md        # Step-by-step deployment guide
    ├── IMPLEMENTATION.md    # Complete architecture & API docs
    └── README.md           # This file
```

## Quick Start

### 1. Install & Deploy (5 minutes)
```bash
cd /home/user/Portfolio-Project/projects-new/P11-serverless-api-gateway
make install
make test
make deploy ENVIRONMENT=dev
```

### 2. Test Your API
```bash
ENDPOINT=$(make endpoint ENVIRONMENT=dev)

# Create item
curl -X POST "https://${ENDPOINT}/items" \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"name": "Item", "description": "Test", "price": 29.99}'

# List items
curl -X GET "https://${ENDPOINT}/items" \
  -H "Authorization: Bearer dev-key-12345"
```

### 3. View Your Results
```bash
# Get CloudWatch logs
aws logs tail /aws/lambda/create-item-dev --follow

# View API endpoint
make endpoint ENVIRONMENT=dev

# Show CloudFormation outputs
make outputs ENVIRONMENT=dev
```

## API Endpoints

All endpoints require `Authorization: Bearer <api-key>` header.

| Method | Path | Description |
|--------|------|-------------|
| POST | /items | Create a new item |
| GET | /items | List all items (with pagination) |
| GET | /items/{id} | Get specific item |
| PUT | /items/{id} | Update item |
| DELETE | /items/{id} | Delete item |

### Example Request/Response

**Create Item (POST /items)**

Request:
```bash
curl -X POST https://api.example.com/dev/items \
  -H "Authorization: Bearer dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "Dell XPS 15",
    "price": 1299.99
  }'
```

Response (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Laptop",
  "description": "Dell XPS 15",
  "price": 1299.99,
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Testing

```bash
# Run all tests
make test

# Run with coverage report
make test-coverage

# Run specific test
pytest tests/test_create.py -v

# Run only integration tests
pytest tests/test_integration.py -v
```

The project includes 22 comprehensive tests covering:
- Item creation with validation
- Reading items by ID and listing
- Updating items with partial updates
- Deletion with proper cleanup
- Error scenarios and edge cases
- Full CRUD workflows
- Concurrent-like operations

## Deployment

### Development (Pay-per-request)
```bash
make deploy ENVIRONMENT=dev
```

### Production (Provisioned capacity)
```bash
make deploy ENVIRONMENT=prod AWS_REGION=us-east-1
```

### Destroy Resources
```bash
make destroy ENVIRONMENT=dev
```

## Make Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make test              # Run all tests
make test-coverage     # Generate coverage report
make lint              # Check code quality
make format            # Format code
make build             # Build SAM application
make deploy            # Deploy to AWS
make destroy           # Delete AWS stack
make endpoint          # Show API endpoint
make outputs           # Show stack outputs
make clean             # Clean build artifacts
```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup and basic testing
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with troubleshooting
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Architecture, API reference, and production details
- **[Makefile](Makefile)** - Build automation and available commands

## Architecture

```
HTTP Request → API Gateway → Lambda Authorizer → Lambda Handler → DynamoDB
                                                       ↓
                                            CloudWatch Logs + X-Ray Tracing
```

Key components:
- **API Gateway**: REST API with authentication
- **Lambda Functions**: Serverless compute for business logic
- **DynamoDB**: NoSQL database with auto-scaling
- **CloudWatch**: Monitoring, logging, and metrics
- **X-Ray**: Distributed tracing for debugging
- **IAM**: Least-privilege role-based access control

## Security Features

- API Key authentication on all endpoints
- Least-privilege IAM roles (DynamoDB, CloudWatch, X-Ray only)
- Input validation on all fields
- Secure logging without sensitive data
- Optional VPC deployment
- Encryption support for DynamoDB

## Performance

- Cold start: ~1-2 seconds (Lambda)
- Typical request latency: 50-200ms
- Auto-scaling on demand (development)
- Provisioned capacity available (production)
- Connection pooling for DynamoDB

## Cost Estimates

**Development Environment (pay-per-request)**
- Free tier: First 1M API requests/month, 25GB DynamoDB storage
- Typical cost: $0-5/month for light usage

**Production Environment (provisioned)**
- DynamoDB: ~$1.25/hour base (5 RCU/5 WCU)
- Lambda: ~$0.20 per 1M requests
- API Gateway: ~$3.50 per 1M requests
- Typical cost: $30-100/month for moderate usage

## Prerequisites

- Python 3.11+
- AWS Account with appropriate permissions
- AWS CLI configured
- Make (for using Makefile targets)
- Optional: SAM CLI for local testing

## Included Artifacts

- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER)
- Producer/job/consumer pipeline demonstration
- Kubernetes deployment stub

## Next Steps

1. **Deploy**: Follow [QUICKSTART.md](QUICKSTART.md)
2. **Monitor**: Set up CloudWatch alarms
3. **Scale**: Adjust Lambda memory and DynamoDB capacity
4. **Secure**: Update API keys and configure VPC
5. **Integrate**: Connect to your application

## Troubleshooting

**401 Unauthorized**: Check API key in Authorization header
```bash
Authorization: Bearer dev-key-12345
```

**404 Not Found**: Verify item ID exists
```bash
curl -X GET "https://${ENDPOINT}/items/${ITEM_ID}" -H "Authorization: Bearer dev-key-12345"
```

**DynamoDB Errors**: Check table name in environment
```bash
aws dynamodb describe-table --table-name items-table-dev
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting steps.

## Production Checklist

- [ ] Update API keys (change from dev-key-12345)
- [ ] Set LOG_LEVEL to INFO or WARN
- [ ] Enable VPC for Lambda functions
- [ ] Configure DynamoDB Point-in-Time Recovery
- [ ] Set up CloudWatch alarms
- [ ] Enable X-Ray tracing for monitoring
- [ ] Add API rate limiting
- [ ] Implement request/response validation
- [ ] Add CORS if needed
- [ ] Review IAM permissions

## Support & Documentation

For detailed information, see:
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment and troubleshooting
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Complete technical reference
- `template.yaml` - Infrastructure definition
- `lambda_handlers/*.py` - Function implementations
- `tests/` - Usage examples

## Project Statistics

- **Lines of Code**: ~1500 (Lambda handlers + tests)
- **Test Coverage**: 22 tests covering all CRUD operations
- **Documentation**: 4 comprehensive guides (Quickstart, Deployment, Implementation, README)
- **Infrastructure**: 1 SAM template with multi-environment support
- **Automation**: 15+ Makefile targets for common tasks

## License & Attribution

This project is part of the Portfolio-Project collection for educational and professional demonstration purposes.

---

**Ready to deploy?** Start with [QUICKSTART.md](QUICKSTART.md) 🚀
