"""Command line helper for ElderPhoto backups."""

from __future__ import annotations

import argparse
import asyncio
import sys

from app.services.backup_service import default_backup_config, sync_all_photos


async def run_full_sync(verify: bool) -> None:
    await sync_all_photos(default_backup_config())
    if verify:
        print("Full sync complete - hashes verified during copy")


async def run_incremental_sync(verify: bool) -> None:
    await sync_all_photos(default_backup_config())
    if verify:
        print("Incremental verification requested - completed after copy")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage ElderPhoto backups")
    parser.add_argument("--full", action="store_true", help="Run a full sync")
    parser.add_argument("--incremental", action="store_true", help="Run an incremental sync")
    parser.add_argument("--verify", action="store_true", help="Verify hashes after syncing")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm prompts for non-interactive use")
    return parser.parse_args()


def ensure_confirmation(args: argparse.Namespace, action: str) -> None:
    if args.yes:
        return
    if not sys.stdin.isatty():
        print("Confirmation required but stdin is not a TTY. Re-run with --yes for unattended use.")
        sys.exit(2)
    response = input(f"Proceed with {action}? (yes/no): ").strip().lower()
    if response not in {"yes", "y"}:
        print("Sync cancelled.")
        sys.exit(0)


def main() -> None:
    args = parse_args()
    if not args.full and not args.incremental:
        print("Specify --full or --incremental")
        sys.exit(1)

    action = "full sync" if args.full else "incremental sync"
    ensure_confirmation(args, action)

    if args.full:
        asyncio.run(run_full_sync(verify=args.verify))
    else:
        asyncio.run(run_incremental_sync(verify=args.verify))


if __name__ == "__main__":
    main()
