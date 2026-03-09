#!/bin/bash
# Initialize LocalStack resources for local development

echo "Initializing LocalStack resources..."

# Create S3 Buckets
awslocal s3 mb s3://input-events
awslocal s3 mb s3://processed-events

# Create SQS Queues
awslocal sqs create-queue --queue-name events-queue
awslocal sqs create-queue --queue-name dlq

# Create DynamoDB Tables
awslocal dynamodb create-table \
    --table-name processing-metrics \
    --attribute-definitions AttributeName=metric_id,AttributeType=S \
    --key-schema AttributeName=metric_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name processing-jobs \
    --attribute-definitions \
        AttributeName=job_id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=job_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=user-index,KeySchema=[{AttributeName=user_id,KeyType=HASH}],Projection={ProjectionType=ALL}" \
    --billing-mode PAY_PER_REQUEST

# Create SNS Topic
awslocal sns create-topic --name notifications

# Create Step Functions State Machine
awslocal stepfunctions create-state-machine \
    --name DataProcessingWorkflow \
    --definition '{
        "Comment": "Data Processing Workflow",
        "StartAt": "ValidateInput",
        "States": {
            "ValidateInput": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:us-east-1:000000000000:function:validate-input",
                "Next": "ProcessData",
                "Catch": [{
                    "ErrorEquals": ["States.ALL"],
                    "Next": "HandleError"
                }]
            },
            "ProcessData": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:us-east-1:000000000000:function:process-data",
                "Next": "StoreResults",
                "Catch": [{
                    "ErrorEquals": ["States.ALL"],
                    "Next": "HandleError"
                }]
            },
            "StoreResults": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:us-east-1:000000000000:function:store-results",
                "End": true,
                "Catch": [{
                    "ErrorEquals": ["States.ALL"],
                    "Next": "HandleError"
                }]
            },
            "HandleError": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:us-east-1:000000000000:function:handle-error",
                "End": true
            }
        }
    }' \
    --role-arn arn:aws:iam::000000000000:role/StepFunctionsRole

echo "LocalStack initialization complete!"
