#!/usr/bin/env python3
"""
Disaster Recovery Drill Script for RDS Multi-AZ Failover Testing.

This script automates RDS failover testing to validate disaster recovery capabilities.
It initiates a failover, monitors the process, and generates a report.

Usage:
    python src/dr_drill.py --db-instance-id my-db-instance [--region us-east-1]

Environment Variables:
    AWS_REGION: AWS region (default: us-east-1)
    AWS_PROFILE: AWS CLI profile to use
"""

import argparse
import boto3
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
from botocore.exceptions import ClientError


class RDSFailoverDrill:
    """Manages RDS Multi-AZ failover drill operations."""

    def __init__(self, region: str = 'us-east-1'):
        """Initialize AWS clients."""
        self.region = region
        self.rds = boto3.client('rds', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)

    def get_db_instance_info(self, db_instance_id: str) -> Dict:
        """
        Get current RDS instance information.

        Args:
            db_instance_id: RDS instance identifier

        Returns:
            Dictionary with instance details
        """
        try:
            response = self.rds.describe_db_instances(
                DBInstanceIdentifier=db_instance_id
            )
            if not response['DBInstances']:
                raise ValueError(f"DB instance {db_instance_id} not found")

            instance = response['DBInstances'][0]
            return {
                'identifier': instance['DBInstanceIdentifier'],
                'status': instance['DBInstanceStatus'],
                'availability_zone': instance['AvailabilityZone'],
                'multi_az': instance['MultiAZ'],
                'engine': instance['Engine'],
                'endpoint': instance.get('Endpoint', {}).get('Address', 'N/A')
            }
        except ClientError as e:
            print(f"Error getting DB instance info: {e}")
            raise

    def check_prerequisites(self, db_instance_id: str) -> bool:
        """
        Check if prerequisites for failover are met.

        Args:
            db_instance_id: RDS instance identifier

        Returns:
            True if prerequisites are met
        """
        info = self.get_db_instance_info(db_instance_id)

        print("Checking prerequisites...")
        print(f"  Instance: {info['identifier']}")
        print(f"  Status: {info['status']}")
        print(f"  Multi-AZ: {info['multi_az']}")
        print(f"  Current AZ: {info['availability_zone']}")

        if not info['multi_az']:
            print("ERROR: Multi-AZ is not enabled. Cannot perform failover.")
            return False

        if info['status'] != 'available':
            print(f"ERROR: Instance status is '{info['status']}', must be 'available'")
            return False

        print("Prerequisites check passed ✓")
        return True

    def initiate_failover(self, db_instance_id: str) -> bool:
        """
        Initiate RDS failover.

        Args:
            db_instance_id: RDS instance identifier

        Returns:
            True if failover initiated successfully
        """
        try:
            print(f"\nInitiating failover for {db_instance_id}...")
            self.rds.reboot_db_instance(
                DBInstanceIdentifier=db_instance_id,
                ForceFailover=True
            )
            print("Failover initiated successfully ✓")
            return True
        except ClientError as e:
            print(f"Error initiating failover: {e}")
            return False

    def monitor_failover(self, db_instance_id: str, max_wait_time: int = 600) -> Dict:
        """
        Monitor failover progress.

        Args:
            db_instance_id: RDS instance identifier
            max_wait_time: Maximum time to wait for failover (seconds)

        Returns:
            Dictionary with failover results
        """
        start_time = time.time()
        initial_info = self.get_db_instance_info(db_instance_id)
        initial_az = initial_info['availability_zone']

        print(f"\nMonitoring failover progress...")
        print(f"Initial AZ: {initial_az}")
        print(f"Max wait time: {max_wait_time} seconds\n")

        check_interval = 15  # Check every 15 seconds
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(check_interval)
            elapsed = int(time.time() - start_time)

            try:
                info = self.get_db_instance_info(db_instance_id)
                status = info['status']
                current_az = info['availability_zone']

                print(f"[{elapsed}s] Status: {status}, AZ: {current_az}")

                if status == 'available' and current_az != initial_az:
                    duration = time.time() - start_time
                    print(f"\n✓ Failover completed successfully!")
                    print(f"  Duration: {duration:.2f} seconds")
                    print(f"  Initial AZ: {initial_az}")
                    print(f"  Final AZ: {current_az}")

                    return {
                        'success': True,
                        'duration': duration,
                        'initial_az': initial_az,
                        'final_az': current_az,
                        'elapsed_time': elapsed
                    }

                if status == 'failed':
                    print(f"\n✗ Failover failed!")
                    return {
                        'success': False,
                        'error': 'Instance entered failed state',
                        'elapsed_time': elapsed
                    }

            except Exception as e:
                print(f"Error monitoring failover: {e}")
                continue

        print(f"\n✗ Failover did not complete within {max_wait_time} seconds")
        return {
            'success': False,
            'error': 'Timeout',
            'elapsed_time': elapsed
        }

    def get_cloudwatch_metrics(self, db_instance_id: str, duration_minutes: int = 30) -> List[Dict]:
        """
        Get CloudWatch metrics during failover.

        Args:
            db_instance_id: RDS instance identifier
            duration_minutes: How far back to look for metrics

        Returns:
            List of metric data points
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time.replace(minute=end_time.minute - duration_minutes)

            metrics = []
            metric_names = [
                'CPUUtilization',
                'DatabaseConnections',
                'ReadLatency',
                'WriteLatency'
            ]

            for metric_name in metric_names:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName=metric_name,
                    Dimensions=[
                        {'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5 minutes
                    Statistics=['Average', 'Maximum']
                )

                if response['Datapoints']:
                    metrics.append({
                        'metric': metric_name,
                        'datapoints': len(response['Datapoints']),
                        'latest': sorted(response['Datapoints'], key=lambda x: x['Timestamp'])[-1]
                    })

            return metrics
        except Exception as e:
            print(f"Error getting CloudWatch metrics: {e}")
            return []

    def generate_report(self, db_instance_id: str, result: Dict, output_file: Optional[str] = None):
        """
        Generate failover drill report.

        Args:
            db_instance_id: RDS instance identifier
            result: Failover result dictionary
            output_file: Optional file path to save report
        """
        report = {
            'drill_timestamp': datetime.utcnow().isoformat(),
            'db_instance_id': db_instance_id,
            'region': self.region,
            'failover_result': result,
            'metrics': self.get_cloudwatch_metrics(db_instance_id)
        }

        # Print report to console
        print("\n" + "=" * 60)
        print("DISASTER RECOVERY DRILL REPORT")
        print("=" * 60)
        print(json.dumps(report, indent=2, default=str))
        print("=" * 60)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\nReport saved to: {output_file}")

        return report

    def run_drill(self, db_instance_id: str, max_wait_time: int = 600, output_file: Optional[str] = None) -> Dict:
        """
        Execute complete DR drill.

        Args:
            db_instance_id: RDS instance identifier
            max_wait_time: Maximum time to wait for failover
            output_file: Optional file path to save report

        Returns:
            Drill report dictionary
        """
        print("=" * 60)
        print("RDS MULTI-AZ FAILOVER DRILL")
        print("=" * 60)
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print(f"DB Instance: {db_instance_id}")
        print(f"Region: {self.region}\n")

        # Check prerequisites
        if not self.check_prerequisites(db_instance_id):
            result = {'success': False, 'error': 'Prerequisites not met'}
            return self.generate_report(db_instance_id, result, output_file)

        # Confirm with user
        print("\nWARNING: This will trigger a production failover event.")
        response = input("Do you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Drill cancelled by user.")
            result = {'success': False, 'error': 'Cancelled by user'}
            return self.generate_report(db_instance_id, result, output_file)

        # Initiate failover
        if not self.initiate_failover(db_instance_id):
            result = {'success': False, 'error': 'Failed to initiate failover'}
            return self.generate_report(db_instance_id, result, output_file)

        # Monitor failover
        result = self.monitor_failover(db_instance_id, max_wait_time)

        # Generate and return report
        return self.generate_report(db_instance_id, result, output_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='RDS Multi-AZ Failover Drill Script',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--db-instance-id',
        required=True,
        help='RDS instance identifier'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    parser.add_argument(
        '--max-wait-time',
        type=int,
        default=600,
        help='Maximum time to wait for failover in seconds (default: 600)'
    )
    parser.add_argument(
        '--output-file',
        help='Output file for drill report (JSON format)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Check prerequisites only, do not initiate failover'
    )

    args = parser.parse_args()

    # Initialize drill manager
    drill = RDSFailoverDrill(region=args.region)

    try:
        if args.dry_run:
            print("DRY RUN MODE - Prerequisites check only\n")
            if drill.check_prerequisites(args.db_instance_id):
                print("\n✓ Instance is ready for failover drill")
                sys.exit(0)
            else:
                print("\n✗ Instance is not ready for failover drill")
                sys.exit(1)
        else:
            # Run full drill
            report = drill.run_drill(
                db_instance_id=args.db_instance_id,
                max_wait_time=args.max_wait_time,
                output_file=args.output_file
            )

            if report['failover_result']['success']:
                sys.exit(0)
            else:
                sys.exit(1)

    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
