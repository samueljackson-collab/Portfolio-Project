#!/usr/bin/env python3
"""Validate Postman collection structure."""
import json
from pathlib import Path
import pytest


@pytest.fixture
def collection_file():
    """Get collection file path."""
    return Path(__file__).parent.parent / "collections" / "api-tests.json"


def test_collection_exists(collection_file):
    """Verify collection file exists."""
    assert collection_file.exists(), f"Collection not found: {collection_file}"


def test_collection_valid_json(collection_file):
    """Verify collection is valid JSON."""
    with open(collection_file) as f:
        data = json.load(f)
    assert data is not None


def test_collection_has_info(collection_file):
    """Verify collection has info section."""
    with open(collection_file) as f:
        data = json.load(f)
    assert "info" in data
    assert "name" in data["info"]
    assert "schema" in data["info"]


def test_collection_has_items(collection_file):
    """Verify collection has test items."""
    with open(collection_file) as f:
        data = json.load(f)
    assert "item" in data
    assert len(data["item"]) > 0


def test_authentication_folder_exists(collection_file):
    """Verify Authentication folder exists."""
    with open(collection_file) as f:
        data = json.load(f)

    auth_folder = next((item for item in data["item"] if item["name"] == "Authentication"), None)
    assert auth_folder is not None
    assert "item" in auth_folder
    assert len(auth_folder["item"]) > 0


def test_requests_have_tests(collection_file):
    """Verify requests have test scripts."""
    with open(collection_file) as f:
        data = json.load(f)

    def check_request_tests(items):
        for item in items:
            if "item" in item:
                check_request_tests(item["item"])
            elif "request" in item:
                events = item.get("event", [])
                test_events = [e for e in events if e.get("listen") == "test"]
                assert len(test_events) > 0, f"Request '{item['name']}' has no tests"

    check_request_tests(data["item"])


def test_environment_template_exists():
    """Verify environment template exists."""
    template = Path(__file__).parent.parent / "collections" / "environment.template.json"
    assert template.exists()


def test_environment_template_valid():
    """Verify environment template is valid."""
    template = Path(__file__).parent.parent / "collections" / "environment.template.json"
    with open(template) as f:
        data = json.load(f)

    assert "values" in data
    assert len(data["values"]) > 0

    # Check required variables
    keys = [v["key"] for v in data["values"]]
    assert "API_BASE_URL" in keys
