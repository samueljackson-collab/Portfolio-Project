#!/usr/bin/env python3
"""
ElderPhoto Backup Synchronization Script

Run this script via cron to periodically sync photos to backup locations.
Can be run manually for initial sync or recovery operations.

Usage:
    # Full sync of all photos
    python backup_sync.py --full

    # Incremental sync (only new/modified files)
    python backup_sync.py --incremental

    # Verify backups without syncing
    python backup_sync.py --verify-only

    # Check backup status
    python backup_sync.py --status

Examples:
    # Daily incremental sync (run via cron)
    0 2 * * * cd /path/to/backend && python scripts/backup_sync.py --incremental

    # Weekly full sync with verification
    0 3 * * 0 cd /path/to/backend && python scripts/backup_sync.py --full --verify

    # Status check every hour
    0 * * * * cd /path/to/backend && python scripts/backup_sync.py --status
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.backup_service import (
    sync_all_photos,
    get_backup_status,
    generate_backup_report,
    verify_backups,
    backup_config,
)


async def run_full_sync(verify: bool = False, auto_confirm: bool = False):
    """
    Perform a full sync of all photos to backup locations.

    Args:
        verify: Whether to verify backups after sync
    """
    print("=" * 60)
    print("ElderPhoto Full Backup Sync")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Show backup locations
    print("Backup Locations:")
    for backup in backup_config.enabled_backups:
        status = "✓ Ready" if backup.is_accessible else "✗ Not Accessible"
        print(f"  {backup.name}: {status}")
    print()

    if auto_confirm:
        print("Auto-confirm enabled; starting full sync without prompting.")
    else:
        response = input("Proceed with full sync? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Sync cancelled.")
            return

    print("\nSyncing photos...")
    print("-" * 60)

    # Run sync
    stats = await sync_all_photos()

    # Print results
    print()
    print("Sync Complete!")
    print("-" * 60)
    print(f"Total Photos:  {stats['total']}")
    print(f"Synced:        {stats['synced']} ✓")
    print(f"Failed:        {stats['failed']} ✗")
    print(f"Skipped:       {stats['skipped']}")
    print()

    # Verify if requested
    if verify:
        await run_verification()

    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


async def run_incremental_sync(verify: bool = False):
    """
    Perform an incremental sync (only new/modified files).

    This is faster than full sync and suitable for cron jobs.
    """
    print("=" * 60)
    print("ElderPhoto Incremental Backup Sync")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # For now, incremental sync is the same as full sync
    # In production, you'd track last sync time and only sync new files
    print("Note: Incremental sync checks all files (full sync)")
    print("      In production, this would only sync files modified since last run")
    print()

    stats = await sync_all_photos()

    print()
    print("Sync Complete!")
    print("-" * 60)
    print(f"Synced: {stats['synced']}/{stats['total']} photos")

    if verify:
        await run_verification()

    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


async def run_status_check():
    """
    Check and display backup status.
    """
    report = await generate_backup_report()
    print(report)


async def run_verification():
    """
    Verify backups without syncing.
    """
    print("=" * 60)
    print("ElderPhoto Backup Verification")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get all photos from primary storage
    primary_path = Path(backup_config.primary.path)

    if not primary_path.exists():
        print(f"Error: Primary storage not found at {primary_path}")
        return

    # Sample verification (check first 100 photos)
    photo_files = list(primary_path.rglob("*.jpg"))[:100]

    if not photo_files:
        print("No photos found to verify.")
        return

    print(f"Verifying {len(photo_files)} photos...")
    print()

    verified = 0
    missing = []

    for photo_file in photo_files:
        relative_path = str(photo_file.relative_to(primary_path))
        results = await verify_backups(relative_path)

        all_ok = all(results.values())
        if all_ok:
            verified += 1
        else:
            missing.append((relative_path, results))

        # Progress indicator
        if verified % 10 == 0:
            print(f"  Verified {verified}/{len(photo_files)}...")

    # Report results
    print()
    print("Verification Complete!")
    print("-" * 60)
    print(f"Verified:  {verified}/{len(photo_files)} ✓")
    print(f"Missing:   {len(missing)} ✗")

    if missing:
        print()
        print("Missing Backups:")
        for path, results in missing[:10]:  # Show first 10
            print(f"  {path}")
            for location, exists in results.items():
                status = "✓" if exists else "✗"
                print(f"    {location}: {status}")

        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    print()
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def main():
    """Main entry point for backup script."""
    parser = argparse.ArgumentParser(
        description="ElderPhoto Backup Synchronization Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform full sync of all photos"
    )

    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Perform incremental sync (new/modified only)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify backups after sync (used with --full or --incremental)"
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify backups, don't sync"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show backup status and exit"
    )

    parser.add_argument(
        "--yes",
        "--assume-yes",
        dest="assume_yes",
        action="store_true",
        help="Run non-interactively and auto-confirm prompts (use for cron jobs)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.full, args.incremental, args.verify_only, args.status]):
        parser.error("Must specify one of: --full, --incremental, --verify-only, or --status")

    non_interactive = not sys.stdin.isatty()

    if args.full and non_interactive and not args.assume_yes:
        print("Error: --full requires --yes when run without an interactive terminal.")
        sys.exit(2)

    # Run appropriate command
    try:
        if args.status:
            asyncio.run(run_status_check())
        elif args.verify_only:
            asyncio.run(run_verification())
        elif args.full:
            confirm_flag = args.assume_yes or non_interactive
            asyncio.run(run_full_sync(verify=args.verify, auto_confirm=confirm_flag))
        elif args.incremental:
            asyncio.run(run_incremental_sync(verify=args.verify))

    except KeyboardInterrupt:
        print("\n\nBackup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
