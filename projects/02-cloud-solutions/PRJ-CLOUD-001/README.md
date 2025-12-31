# Serverless Data API (PRJ-CLOUD-001)

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../../DOCUMENTATION_INDEX.md).


**Status:** 🟢 Planned

## Overview

This project delivers a small AWS serverless REST API that demonstrates cloud solution patterns, including IAM least privilege, environment-specific configuration, and automated deployments. It uses the Serverless Framework to orchestrate Lambda functions, API Gateway routing, and DynamoDB data persistence while keeping all infrastructure as code.

## Architecture

- **API Gateway** exposes `POST /items` and `GET /items/{id}` routes.
- **AWS Lambda** handlers perform create and read operations.
- **DynamoDB** stores item records with strong consistency options for reads.
- **CloudWatch Logs** capture structured JSON logs for observability.
- **Serverless Framework** manages packaging, deployment, and environment variables.

## Deployment

1. Install the Serverless Framework CLI and authenticate with AWS using an IAM role that supports CloudFormation deployments.
2. Configure the `AWS_PROFILE` or environment-based credentials for the target account.
3. Run `npm install` to install runtime and dev dependencies for the handlers and tests.
4. Deploy the stack with `serverless deploy --stage dev` or `sls deploy --stage prod`.
5. Validate endpoints with `curl` or a REST client, ensuring HTTP 201 on creation and 200 on reads.

## Local Development

- Use `npm run lint` to check for code quality issues.
- Run `npm test` to execute the unit tests under `tests/unit`.
- Leverage `sls invoke local -f create` to exercise the Lambda handler with local payloads.
- Update the `serverless.yml` file to add new resources (e.g., DLQ, alarms) following AWS best practices.

## Future Enhancements

- Add request validation with API Gateway models and Lambda Powertools for observability.
- Implement CI/CD via GitHub Actions to lint, test, and deploy on merge.
- Introduce fine-grained IAM policies for DynamoDB access per stage.

## Contact

For questions, reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).
