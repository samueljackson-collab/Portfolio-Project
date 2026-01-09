#!/usr/bin/env python3
"""GitHub PR cleanup utility.

Usage examples:
  python scripts/github_pr_cleanup.py --list
  python scripts/github_pr_cleanup.py --dry-run --close-stale --days 30
  python scripts/github_pr_cleanup.py --close-stale --days 90 --max 200
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
    """Check rate limit headers and warn if approaching limit."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    limit = response.headers.get("X-RateLimit-Limit")

    if remaining is not None and limit is not None:
        try:
            remaining_int = int(remaining)
            limit_int = int(limit)

            if remaining_int < 10:
                print(
                    f"WARNING: Approaching rate limit. "
                    f"Remaining: {remaining_int}/{limit_int} requests."
                )
        except (ValueError, TypeError):
            # Ignore invalid rate limit headers
            pass


def make_github_request(
    method: str,
    url: str,
    headers: dict,
    max_retries: int = 3,
    **kwargs,
) -> requests.Response:
    """Make a GitHub API request with retry logic and rate limit handling."""
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, headers=headers, **kwargs)

            # Check rate limit and warn if approaching limit
            check_rate_limit(response)

            # Handle rate limit errors (429) with exponential backoff
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except (ValueError, TypeError):
                            # Fallback to exponential backoff if Retry-After is invalid
                            wait_time = 2**attempt
                    else:
                        # Exponential backoff: 2^attempt seconds
                        wait_time = 2**attempt

                    reset_time = response.headers.get("X-RateLimit-Reset")
                    reset_info = ""
                    if reset_time:
                        try:
                            reset_timestamp = int(reset_time)
                            reset_datetime = datetime.fromtimestamp(
                                reset_timestamp, tz=timezone.utc
                            )
                            reset_info = (
                                f" Rate limit resets at {reset_datetime.isoformat()}."
                            )
                        except (ValueError, TypeError):
                            pass

                    print(
                        f"Rate limited (429). Waiting {wait_time} seconds before retry "
                        f"(attempt {attempt + 1}/{max_retries})...{reset_info}"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    # Final attempt failed, provide detailed error message
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        try:
                            reset_timestamp = int(reset_time)
                            reset_datetime = datetime.fromtimestamp(
                                reset_timestamp, tz=timezone.utc
                            )
                            current_timestamp = int(
                                datetime.now(timezone.utc).timestamp()
                            )
                            wait_seconds = max(0, reset_timestamp - current_timestamp)
                            raise SystemExit(
                                f"GitHub API rate limit exceeded after {max_retries} retries. "
                                f"Rate limit resets at {reset_datetime.isoformat()} "
                                f"(in {wait_seconds} seconds). Please try again later."
                            )
                        except (ValueError, TypeError):
                            pass

                    raise SystemExit(
                        f"GitHub API rate limit exceeded after {max_retries} retries. "
                        "Please try again later."
                    )

            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as exc:
            # Only retry on server errors (5xx), not client errors (4xx)
            if (
                attempt < max_retries - 1
                and exc.response is not None
                and exc.response.status_code >= 500
            ):
                wait_time = 2**attempt
                print(
                    f"Server error ({exc.response.status_code}). "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
                continue
            raise
        except requests.exceptions.RequestException as exc:
            # Retry on network errors with exponential backoff
            if attempt < max_retries - 1:
                wait_time = 2**attempt
                print(f"Request failed: {exc}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            raise


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
    make_github_request(
        "PATCH",
        f"https://api.github.com/repos/{repo}/pulls/{pr.number}",
        headers=github_headers(token),
        json={"state": "closed"},
        timeout=30,
    )


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


def main() -> None:
    args = parse_args()
    token = get_env("GITHUB_TOKEN")
    repo = get_env("GITHUB_REPO")

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
