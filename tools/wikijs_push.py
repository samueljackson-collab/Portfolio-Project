#!/usr/bin/env python3
"""
Wiki.js API Push Script - Enterprise Portfolio
Automatically publishes Markdown documentation to Wiki.js via GraphQL API
"""

import os
import sys
import glob
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: requests module not found")
    print("Install with: pip install requests")
    sys.exit(1)

# Configuration
API_URL = os.getenv("WIKI_URL", "http://localhost:3000/graphql")
API_TOKEN = os.getenv("WIKI_TOKEN", "")
BASE_PATH = os.getenv("WIKI_BASE_PATH", "/projects")

# GraphQL mutations
UPSERT_PAGE_MUTATION = """
mutation CreateOrUpdatePage($title: String!, $content: String!, $path: String!, $locale: String!) {
  pages {
    create(
      content: $content
      description: ""
      editor: "markdown"
      isPublished: true
      isPrivate: false
      locale: $locale
      path: $path
      tags: []
      title: $title
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        path
        title
      }
    }
  }
}
"""

UPDATE_PAGE_MUTATION = """
mutation UpdatePage($id: Int!, $title: String!, $content: String!, $path: String!) {
  pages {
    update(
      id: $id
      content: $content
      description: ""
      editor: "markdown"
      isPublished: true
      isPrivate: false
      path: $path
      tags: []
      title: $title
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        path
        title
      }
    }
  }
}
"""

GET_PAGE_QUERY = """
query GetPage($path: String!) {
  pages {
    single(path: $path) {
      id
      path
      title
    }
  }
}
"""


class WikiJSPublisher:
    """Publishes Markdown files to Wiki.js"""

    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def graphql_request(self, query: str, variables: Dict) -> Dict:
        """Execute a GraphQL request"""
        payload = {
            "query": query,
            "variables": variables
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making GraphQL request: {e}")
            raise

    def get_page(self, path: str) -> Optional[Dict]:
        """Check if a page already exists"""
        result = self.graphql_request(GET_PAGE_QUERY, {"path": path})

        if result.get("data", {}).get("pages", {}).get("single"):
            return result["data"]["pages"]["single"]
        return None

    def create_page(self, title: str, content: str, path: str, locale: str = "en") -> bool:
        """Create a new page"""
        variables = {
            "title": title,
            "content": content,
            "path": path,
            "locale": locale
        }

        result = self.graphql_request(UPSERT_PAGE_MUTATION, variables)
        response_result = result.get("data", {}).get("pages", {}).get("create", {}).get("responseResult", {})

        if response_result.get("succeeded"):
            print(f"✓ Created: {title} → {path}")
            return True
        else:
            error = response_result.get("message", "Unknown error")
            print(f"✗ Failed to create {title}: {error}")
            return False

    def update_page(self, page_id: int, title: str, content: str, path: str) -> bool:
        """Update an existing page"""
        variables = {
            "id": page_id,
            "title": title,
            "content": content,
            "path": path
        }

        result = self.graphql_request(UPDATE_PAGE_MUTATION, variables)
        response_result = result.get("data", {}).get("pages", {}).get("update", {}).get("responseResult", {})

        if response_result.get("succeeded"):
            print(f"✓ Updated: {title} → {path}")
            return True
        else:
            error = response_result.get("message", "Unknown error")
            print(f"✗ Failed to update {title}: {error}")
            return False

    def publish_file(self, md_path: Path, base_path: str = "/projects") -> bool:
        """Publish a single Markdown file"""
        # Extract title from filename
        title = md_path.stem.replace("-", " ").replace("_", " ").title()

        # Generate Wiki.js path
        relative_path = md_path.relative_to(md_path.parents[len(md_path.parents) - 1])
        wiki_path = f"{base_path}/{md_path.stem}"

        # Read content
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"✗ Error reading {md_path}: {e}")
            return False

        # Check if page exists
        existing_page = self.get_page(wiki_path)

        if existing_page:
            # Update existing page
            return self.update_page(
                page_id=existing_page["id"],
                title=title,
                content=content,
                path=wiki_path
            )
        else:
            # Create new page
            return self.create_page(
                title=title,
                content=content,
                path=wiki_path
            )

    def publish_directory(self, directory: Path, pattern: str = "*.md", base_path: str = "/projects") -> Dict[str, int]:
        """Publish all Markdown files in a directory"""
        stats = {"success": 0, "failed": 0, "skipped": 0}

        markdown_files = list(directory.glob(pattern))

        if not markdown_files:
            print(f"No Markdown files found in {directory}")
            return stats

        print(f"\nPublishing {len(markdown_files)} file(s) from {directory}...\n")

        for md_file in markdown_files:
            # Skip README files (usually contain repo-specific info)
            if md_file.name.upper() == "README.MD":
                print(f"⊘ Skipped: {md_file.name} (README)")
                stats["skipped"] += 1
                continue

            if self.publish_file(md_file, base_path):
                stats["success"] += 1
            else:
                stats["failed"] += 1

        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Publish Markdown documentation to Wiki.js"
    )
    parser.add_argument(
        "path",
        help="Path to Markdown file or directory"
    )
    parser.add_argument(
        "--pattern",
        default="*.md",
        help="File pattern for directory publishing (default: *.md)"
    )
    parser.add_argument(
        "--base-path",
        default=BASE_PATH,
        help=f"Base path in Wiki.js (default: {BASE_PATH})"
    )
    parser.add_argument(
        "--api-url",
        default=API_URL,
        help=f"Wiki.js GraphQL API URL (default: {API_URL})"
    )
    parser.add_argument(
        "--api-token",
        default=API_TOKEN,
        help="Wiki.js API token (or set WIKI_TOKEN env var)"
    )

    args = parser.parse_args()

    # Validate API token
    if not args.api_token:
        print("Error: API token required")
        print("Set WIKI_TOKEN environment variable or use --api-token")
        sys.exit(1)

    # Create publisher
    publisher = WikiJSPublisher(args.api_url, args.api_token)

    # Publish
    path = Path(args.path)

    if path.is_file():
        # Publish single file
        print(f"\nPublishing single file: {path}\n")
        success = publisher.publish_file(path, args.base_path)
        sys.exit(0 if success else 1)

    elif path.is_dir():
        # Publish directory
        stats = publisher.publish_directory(path, args.pattern, args.base_path)

        print("\n" + "=" * 50)
        print("Summary:")
        print(f"  Success: {stats['success']}")
        print(f"  Failed:  {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        print("=" * 50 + "\n")

        sys.exit(0 if stats["failed"] == 0 else 1)

    else:
        print(f"Error: Path not found: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
