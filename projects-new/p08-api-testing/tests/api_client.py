"""
API Client Helper Module

Provides a reusable HTTP client for API testing with built-in authentication
and request methods.
"""

import requests
from typing import Dict, Any, Optional


class APIClient:
    """Helper class for making authenticated API requests"""

    def __init__(self, base_url: str, auth_token: str):
        """
        Initialize API client with base URL and authentication token

        Args:
            base_url: Base URL of the API (e.g., http://localhost:8080)
            auth_token: Bearer token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        })

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        """Make GET request to endpoint"""
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params)

    def post(self, endpoint: str, json: Dict[str, Any]):
        """Make POST request to endpoint"""
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, json=json)

    def put(self, endpoint: str, json: Dict[str, Any]):
        """Make PUT request to endpoint"""
        url = f"{self.base_url}{endpoint}"
        return self.session.put(url, json=json)

    def patch(self, endpoint: str, json: Dict[str, Any]):
        """Make PATCH request to endpoint"""
        url = f"{self.base_url}{endpoint}"
        return self.session.patch(url, json=json)

    def delete(self, endpoint: str):
        """Make DELETE request to endpoint"""
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url)

    def close(self):
        """Close the HTTP session"""
        self.session.close()
