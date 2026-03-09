"""Lambda authorizer for API Gateway authentication."""

import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Retrieve allowed API keys from environment variable
ALLOWED_API_KEYS = os.environ.get("ALLOWED_API_KEYS", "").split(",")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """
    Custom Lambda authorizer for API Gateway.

    Validates API Key from Authorization header.
    Expected header: Authorization: Bearer <api-key>
    """
    auth_token = event.get("authorizationToken", "")
    method_arn = event.get("methodArn", "")

    logger.info(f"Authorizing token for method: {method_arn}")

    try:
        # Extract token (format: "Bearer <token>")
        if not auth_token.startswith("Bearer "):
            logger.warning("Invalid authorization header format")
            raise Exception("Unauthorized")

        api_key = auth_token.split(" ", 1)[1]

        # Validate API key
        if api_key.strip() not in ALLOWED_API_KEYS:
            logger.warning(f"Invalid API key: {api_key[:10]}...")
            raise Exception("Unauthorized")

        # Generate policy
        policy = generate_policy("user", "Allow", method_arn)
        policy["context"] = {
            "api_key": api_key,
            "timestamp": event.get("requestTime", ""),
        }

        logger.info("Authorization successful")
        return policy

    except Exception as e:
        logger.error(f"Authorization failed: {str(e)}")
        raise Exception("Unauthorized")


def generate_policy(principal_id: str, effect: str, resource: str) -> Dict:
    """Generate IAM policy for API Gateway."""
    auth_response = {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        },
    }
    return auth_response
