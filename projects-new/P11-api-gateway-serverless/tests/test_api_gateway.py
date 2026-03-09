"""
Tests for P11 API Gateway Serverless simulation.

Covers:
- Lambda handler logic
- API Gateway request/response structure
- Artifact generation
- Edge cases (missing user, empty path)
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import lambda_handler, simulate_api_gateway_request, main


class TestLambdaHandler:
    """Unit tests for the core lambda handler function."""

    def test_returns_dict(self):
        """Handler must return a dictionary."""
        result = lambda_handler({"user": "tester", "path": "/test"})
        assert isinstance(result, dict)

    def test_response_contains_timestamp(self):
        """Response must include a UTC ISO-8601 timestamp."""
        result = lambda_handler({"user": "tester"})
        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")

    def test_response_contains_input(self):
        """Response must echo the original input."""
        event = {"user": "engineer", "path": "/items"}
        result = lambda_handler(event)
        assert result["input"] == event

    def test_response_contains_response_message(self):
        """Response must contain a greeting message."""
        result = lambda_handler({"user": "sam"})
        assert "response" in result
        assert "sam" in result["response"]

    def test_default_user_when_missing(self):
        """When user key is absent, handler defaults to 'guest'."""
        result = lambda_handler({})
        assert "guest" in result["response"]

    def test_custom_user_in_message(self):
        """Named user should appear in the response message."""
        result = lambda_handler({"user": "platform-team"})
        assert "platform-team" in result["response"]


class TestApiGatewaySimulation:
    """Tests for the API Gateway request simulation wrapper."""

    def test_returns_valid_http_response(self):
        """Simulated response must match API Gateway response shape."""
        response = simulate_api_gateway_request("/hello", "tester")
        assert "statusCode" in response
        assert "headers" in response
        assert "body" in response

    def test_status_code_200(self):
        """Successful simulation must return HTTP 200."""
        response = simulate_api_gateway_request("/hello", "tester")
        assert response["statusCode"] == 200

    def test_content_type_header(self):
        """Response must include application/json content type."""
        response = simulate_api_gateway_request("/health", "ops")
        assert response["headers"]["Content-Type"] == "application/json"

    def test_body_is_valid_json(self):
        """Response body must be a valid JSON string."""
        response = simulate_api_gateway_request("/api/items", "developer")
        try:
            parsed = json.loads(response["body"])
        except json.JSONDecodeError:
            pytest.fail("Response body is not valid JSON")
        assert isinstance(parsed, dict)

    def test_body_contains_lambda_response(self):
        """Parsed body must contain the lambda handler output."""
        response = simulate_api_gateway_request("/api/test", "engineer")
        parsed = json.loads(response["body"])
        assert "timestamp" in parsed
        assert "input" in parsed
        assert "response" in parsed

    def test_path_is_passed_through(self):
        """The requested path must appear in the lambda input."""
        response = simulate_api_gateway_request("/api/products", "buyer")
        parsed = json.loads(response["body"])
        assert parsed["input"]["path"] == "/api/products"

    def test_user_is_passed_through(self):
        """The user must appear in the lambda input."""
        response = simulate_api_gateway_request("/api/profile", "alice")
        parsed = json.loads(response["body"])
        assert parsed["input"]["user"] == "alice"

    def test_http_method_is_get(self):
        """Default HTTP method must be GET."""
        response = simulate_api_gateway_request("/health", "monitor")
        parsed = json.loads(response["body"])
        assert parsed["input"]["httpMethod"] == "GET"


class TestArtifactGeneration:
    """Tests that verify artifact file creation."""

    def test_main_creates_artifact(self, tmp_path, monkeypatch):
        """Running main() must produce an artifact JSON file."""
        import app as app_module

        original_artifact = app_module.ARTIFACT
        artifact_path = tmp_path / "api_gateway_flow.json"
        monkeypatch.setattr(app_module, "ARTIFACT", artifact_path)

        app_module.main()

        assert artifact_path.exists(), "Artifact file was not created"
        assert artifact_path.stat().st_size > 0, "Artifact file is empty"

        app_module.ARTIFACT = original_artifact

    def test_artifact_contains_valid_json(self, tmp_path, monkeypatch):
        """Artifact file must contain parseable JSON."""
        import app as app_module

        artifact_path = tmp_path / "api_gateway_flow.json"
        monkeypatch.setattr(app_module, "ARTIFACT", artifact_path)

        app_module.main()

        content = artifact_path.read_text()
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        assert "statusCode" in parsed

        app_module.ARTIFACT = Path("artifacts/api_gateway_flow.json")

    def test_artifact_status_code_200(self, tmp_path, monkeypatch):
        """Artifact must record an HTTP 200 status code."""
        import app as app_module

        artifact_path = tmp_path / "api_gateway_flow.json"
        monkeypatch.setattr(app_module, "ARTIFACT", artifact_path)

        app_module.main()

        parsed = json.loads(artifact_path.read_text())
        assert parsed["statusCode"] == 200

        app_module.ARTIFACT = Path("artifacts/api_gateway_flow.json")
