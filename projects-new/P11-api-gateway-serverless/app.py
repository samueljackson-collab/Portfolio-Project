from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json

ARTIFACT = Path("artifacts/api_gateway_flow.json")
ARTIFACT.parent.mkdir(exist_ok=True)


def lambda_handler(event: dict) -> dict:
    message = f"Hello {event.get('user', 'guest')} from Lambda"
    audit = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input": event,
        "response": message,
    }
    return audit


def simulate_api_gateway_request(path: str, user: str) -> dict:
    event = {"path": path, "user": user, "httpMethod": "GET"}
    lambda_result = lambda_handler(event)
    gateway_response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(lambda_result),
    }
    return gateway_response


def main():
    request_path = "/hello"
    user = "platform-engineer"
    response = simulate_api_gateway_request(request_path, user)
    ARTIFACT.write_text(json.dumps(response, indent=2))
    print("API Gateway demo complete. Response written to artifacts/api_gateway_flow.json")


if __name__ == "__main__":
    main()
