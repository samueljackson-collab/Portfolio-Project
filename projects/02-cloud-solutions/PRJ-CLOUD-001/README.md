# Serverless CRUD API (PRJ-CLOUD-001)

This project introduces a lightweight serverless CRUD API backed by Amazon DynamoDB. It demonstrates how to combine the Serverless Framework, AWS Lambda, and DynamoDB to deliver a quick-start cloud solution for portfolio examples.

## Architecture Overview
- **API Gateway (HTTP API)** fronts Lambda functions that handle create and read operations.
- **AWS Lambda** functions live in `src/handlers` and encapsulate business logic.
- **DynamoDB** stores items keyed by a unique identifier.
- **Infrastructure-as-Code** uses `serverless.yml` to define the service, provider configuration, functions, IAM permissions, and DynamoDB resources.

## Getting Started
1. Install the Serverless Framework and dependencies.
2. Set the `AWS_PROFILE` environment variable or rely on your default credentials.
3. Deploy the stack: `serverless deploy --stage dev`.
4. Use the printed HTTP endpoints to create and read records.

## Project Structure
- `serverless.yml` — Service, provider, function definitions, and DynamoDB table resource.
- `src/handlers/create.js` — Lambda handler that writes an item to DynamoDB.
- `src/handlers/read.js` — Lambda handler that retrieves an item by ID.
- `tests/unit` — Optional Jest tests validating handler shape and basic behavior.

## Expected Keywords Checklist
- **Service Definition**: `service`, `frameworkVersion`, and `plugins` entries exist.
- **Provider Settings**: includes `name`, `runtime`, `region`, `stage`, `environment`, and `iamRoleStatements`.
- **Functions**: `create` and `read` functions expose `handler`, `events`, and request/response configuration.
- **DynamoDB Integration**: resources include a DynamoDB table with `BillingMode`, `AttributeDefinitions`, `KeySchema`, and a table name that matches handler environment variables.

Ensure you review and adjust configuration values (regions, stages, and naming) before deployment.
