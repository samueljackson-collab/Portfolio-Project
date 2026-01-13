#!/usr/bin/env python3
"""GitHub PR cleanup utility.

Usage examples:
  python scripts/github_pr_cleanup.py --list
  python scripts/github_pr_cleanup.py --dry-run --close-stale --days 30
  python scripts/github_pr_cleanup.py --close-stale --days 90 --max 200

Environment:
  This script requires the following environment variables:

    GITHUB_TOKEN
      A GitHub personal access token used to authenticate API requests.
      You can create a token from:
        https://github.com/settings/tokens
      For classic tokens, grant at least the "repo" scope for private
      repositories, or appropriate fine-grained permissions to read and
      modify pull requests in the target repository.

    GITHUB_REPO
      The repository to operate on, in "owner/repo" format, for example:
        octocat/Hello-World
"""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional

import requests


@dataclass
class PullRequest:
    number: int
    title: str
    updated_at: datetime
    html_url: str

    @property
    def age_days(self) -> int:
        return (datetime.now(timezone.utc) - self.updated_at).days


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Close or list stale GitHub pull requests."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List open pull requests.")
    group.add_argument(
        "--close-stale", action="store_true", help="Close stale pull requests."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview actions without closing PRs."
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Staleness threshold in days."
    )
    parser.add_argument("--max", type=int, default=None, help="Maximum PRs to close.")
    return parser.parse_args()


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def github_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def check_rate_limit(response: requests.Response) -> None:
    """Check rate limit headers and wait if necessary."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset_time = response.headers.get("X-RateLimit-Reset")

    if remaining is not None:
        try:
            remaining_int = int(remaining)
            if remaining_int < 10 and reset_time is not None:
                reset_timestamp = int(reset_time)
                current_time = int(time.time())
                wait_time = max(0, reset_timestamp - current_time)
                if wait_time > 0:
                    print(
                        f"Rate limit nearly exhausted ({remaining} remaining). Waiting {wait_time}s until reset..."
                    )
                    time.sleep(wait_time + 1)  # Add 1 second buffer
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers
            pass


def make_github_request(
    method: str,
    url: str,
    headers: dict,
    max_retries: int = 3,
    **kwargs,
) -> requests.Response:
    """Make a GitHub API request with rate limiting and retry logic."""
    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, **kwargs)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for rate limiting before raising for status
            if response.status_code == 403:
                # Check if it's a rate limit error
                try:
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    reset_time_str = response.headers.get("X-RateLimit-Reset")
                    if (
                        remaining is not None
                        and int(remaining) == 0
                        and reset_time_str is not None
                    ):
                        reset_time = int(reset_time_str)
                        current_time = int(time.time())
                        wait_time = max(0, reset_time - current_time) + 1
                        print(
                            f"Rate limit exceeded. Waiting {wait_time}s until reset..."
                        )
                        time.sleep(wait_time)
                        continue  # Retry the request
                except (ValueError, TypeError):
                    # If headers are malformed, let normal error handling proceed
                    pass

            response.raise_for_status()
            check_rate_limit(response)
            return response

        except requests.exceptions.RequestException as exc:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff
            backoff_time = 2**attempt
            print(
                f"Request failed (attempt {attempt + 1}/{max_retries}): {exc}. Retrying in {backoff_time}s..."
            )
            time.sleep(backoff_time)

    # This line is unreachable but satisfies type checkers
    raise AssertionError("Unreachable code")


def fetch_open_prs(token: str, repo: str) -> List[PullRequest]:
    prs: List[PullRequest] = []
    page = 1
    while True:
        try:
            response = make_github_request(
                "GET",
                f"https://api.github.com/repos/{repo}/pulls",
                headers=github_headers(token),
                params={"state": "open", "per_page": 100, "page": page},
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            raise SystemExit(
                f"Failed to fetch open PRs for repo '{repo}' (page {page}): {exc}"
            ) from exc
        data = response.json()
        if not data:
            break
        for item in data:
            updated_at = datetime.fromisoformat(
                item["updated_at"].replace("Z", "+00:00")
            )
            prs.append(
                PullRequest(
                    number=item["number"],
                    title=item["title"],
                    updated_at=updated_at,
                    html_url=item["html_url"],
                )
            )
        page += 1
    return prs


def list_prs(prs: Iterable[PullRequest]) -> None:
    for pr in prs:
        print(f"#{pr.number} | {pr.age_days} days | {pr.title} | {pr.html_url}")


def stale_prs(prs: Iterable[PullRequest], days: int) -> List[PullRequest]:
    return [pr for pr in prs if pr.age_days >= days]


def close_pr(token: str, repo: str, pr: PullRequest) -> None:
    try:
        response = requests.patch(
            f"https://api.github.com/repos/{repo}/pulls/{pr.number}",
            headers=github_headers(token),
            json={"state": "closed"},
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise SystemExit(
            f"Failed to close PR #{pr.number} ({pr.title!r}): {exc}"
        ) from exc


def close_prs(
    token: str,
    repo: str,
    prs: List[PullRequest],
    dry_run: bool,
    max_count: Optional[int],
) -> None:
    targets = prs if max_count is None else prs[:max_count]
    for pr in targets:
        if dry_run:
            print(f"DRY RUN: Would close #{pr.number} ({pr.age_days} days) {pr.title}")
        else:
            print(f"Closing #{pr.number} ({pr.age_days} days) {pr.title}")
            close_pr(token, repo, pr)


def validate_github_repo(repo: str) -> str:
    """
    Validate that the repository identifier is in the 'owner/repo' format.

    Raises:
        ValueError: If the repository string is not in the expected format.
    """
    owner, sep, name = repo.partition("/")
    if sep != "/" or not owner or not name or "/" in name:
        raise ValueError(
            f"Invalid GITHUB_REPO value: {repo!r}. Expected format 'owner/repo'."
        )
    return repo


def main() -> None:
    args = parse_args()
    token = get_env("GITHUB_TOKEN")
    repo_raw = get_env("GITHUB_REPO")
    repo = validate_github_repo(repo_raw)

    open_prs = fetch_open_prs(token, repo)
    open_prs.sort(key=lambda pr: pr.updated_at)

    if args.list:
        list_prs(open_prs)

    if args.close_stale:
        stale = stale_prs(open_prs, args.days)
        if not stale:
            print(f"No PRs older than {args.days} days.")
            return
        close_prs(token, repo, stale, args.dry_run, args.max)

    if not args.list and not args.close_stale:
        print("No action specified. Use --list or --close-stale.")


if __name__ == "__main__":
    main()
