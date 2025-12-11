#!/usr/bin/env python3
"""
Disaster Recovery Automation Script

Automates backup, snapshot, and restore operations for DR scenarios.
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List


class DRAutomation:
    """Automates disaster recovery operations."""

    def __init__(self, primary_region='us-east-1', dr_region='us-west-2'):
        """Initialize DR automation."""
        self.primary_region = primary_region
        self.dr_region = dr_region

        self.ec2_primary = boto3.client('ec2', region_name=primary_region)
        self.ec2_dr = boto3.client('ec2', region_name=dr_region)
        self.rds_primary = boto3.client('rds', region_name=primary_region)
        self.rds_dr = boto3.client('rds', region_name=dr_region)
        self.s3 = boto3.client('s3')

    def create_ami_snapshots(self, instance_ids: List[str]) -> List[Dict]:
        """Create AMI snapshots of EC2 instances."""
        print(f"Creating AMI snapshots for {len(instance_ids)} instances...")

        snapshots = []
        for instance_id in instance_ids:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            image_name = f"DR-Snapshot-{instance_id}-{timestamp}"

            try:
                response = self.ec2_primary.create_image(
                    InstanceId=instance_id,
                    Name=image_name,
                    Description=f"DR snapshot created on {timestamp}",
                    NoReboot=True
                )

                snapshots.append({
                    'instance_id': instance_id,
                    'ami_id': response['ImageId'],
                    'timestamp': timestamp
                })

                print(f"✓ Created AMI {response['ImageId']} for {instance_id}")
            except Exception as e:
                print(f"✗ Failed to create AMI for {instance_id}: {e}")

        return snapshots

    def copy_snapshots_to_dr_region(self, snapshot_ids: List[str]) -> List[Dict]:
        """Copy EBS snapshots to DR region."""
        print(f"Copying {len(snapshot_ids)} snapshots to DR region...")

        copied = []
        for snap_id in snapshot_ids:
            try:
                response = self.ec2_dr.copy_snapshot(
                    SourceRegion=self.primary_region,
                    SourceSnapshotId=snap_id,
                    Description=f"DR copy from {self.primary_region}"
                )

                copied.append({
                    'source_snapshot': snap_id,
                    'destination_snapshot': response['SnapshotId'],
                    'region': self.dr_region
                })

                print(f"✓ Copied {snap_id} to {response['SnapshotId']}")
            except Exception as e:
                print(f"✗ Failed to copy {snap_id}: {e}")

        return copied

    def create_rds_snapshot(self, db_instance_id: str) -> Dict:
        """Create RDS snapshot."""
        print(f"Creating RDS snapshot for {db_instance_id}...")

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        snapshot_id = f"dr-snapshot-{db_instance_id}-{timestamp}"

        try:
            response = self.rds_primary.create_db_snapshot(
                DBSnapshotIdentifier=snapshot_id,
                DBInstanceIdentifier=db_instance_id
            )

            print(f"✓ Created RDS snapshot {snapshot_id}")

            return {
                'db_instance': db_instance_id,
                'snapshot_id': snapshot_id,
                'timestamp': timestamp,
                'status': response['DBSnapshot']['Status']
            }
        except Exception as e:
            print(f"✗ Failed to create RDS snapshot: {e}")
            return {}

    def copy_rds_snapshot_to_dr_region(self, snapshot_id: str) -> Dict:
        """Copy RDS snapshot to DR region."""
        print(f"Copying RDS snapshot {snapshot_id} to DR region...")

        dr_snapshot_id = f"{snapshot_id}-dr"

        try:
            response = self.rds_dr.copy_db_snapshot(
                SourceDBSnapshotIdentifier=f"arn:aws:rds:{self.primary_region}:*:snapshot:{snapshot_id}",
                TargetDBSnapshotIdentifier=dr_snapshot_id,
                SourceRegion=self.primary_region
            )

            print(f"✓ Copied RDS snapshot to {dr_snapshot_id}")

            return {
                'source_snapshot': snapshot_id,
                'destination_snapshot': dr_snapshot_id,
                'region': self.dr_region
            }
        except Exception as e:
            print(f"✗ Failed to copy RDS snapshot: {e}")
            return {}

    def restore_rds_from_snapshot(self, snapshot_id: str, new_instance_id: str) -> Dict:
        """Restore RDS instance from snapshot."""
        print(f"Restoring RDS from snapshot {snapshot_id}...")

        try:
            response = self.rds_dr.restore_db_instance_from_db_snapshot(
                DBInstanceIdentifier=new_instance_id,
                DBSnapshotIdentifier=snapshot_id
            )

            print(f"✓ Restoring RDS instance {new_instance_id}")

            return {
                'instance_id': new_instance_id,
                'snapshot': snapshot_id,
                'status': response['DBInstance']['DBInstanceStatus']
            }
        except Exception as e:
            print(f"✗ Failed to restore RDS: {e}")
            return {}

    def cleanup_old_snapshots(self, retention_days=30):
        """Delete snapshots older than retention period."""
        print(f"Cleaning up snapshots older than {retention_days} days...")

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted = []

        # Clean EC2 snapshots
        snapshots = self.ec2_primary.describe_snapshots(OwnerIds=['self'])
        for snap in snapshots['Snapshots']:
            if snap['StartTime'].replace(tzinfo=None) < cutoff_date:
                try:
                    self.ec2_primary.delete_snapshot(SnapshotId=snap['SnapshotId'])
                    deleted.append(snap['SnapshotId'])
                    print(f"✓ Deleted snapshot {snap['SnapshotId']}")
                except Exception as e:
                    print(f"✗ Failed to delete {snap['SnapshotId']}: {e}")

        print(f"Cleaned up {len(deleted)} old snapshots")

        return deleted

    def generate_dr_report(self, output_file='dr_report.json'):
        """Generate DR status report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'primary_region': self.primary_region,
            'dr_region': self.dr_region,
            'snapshots': {
                'ec2_snapshots': len(self.ec2_primary.describe_snapshots(OwnerIds=['self'])['Snapshots']),
                'rds_snapshots': len(self.rds_primary.describe_db_snapshots()['DBSnapshots'])
            }
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"Report saved to {output_file}")

        return report


def main():
    """Main entry point."""
    dr = DRAutomation()

    print("=" * 60)
    print("DISASTER RECOVERY AUTOMATION")
    print("=" * 60)

    # Example: Create and copy snapshots
    # dr.create_ami_snapshots(['i-1234567890'])
    # dr.create_rds_snapshot('my-db-instance')
    # dr.cleanup_old_snapshots(30)

    dr.generate_dr_report()

    print("\nDR automation completed")


if __name__ == '__main__':
    main()
