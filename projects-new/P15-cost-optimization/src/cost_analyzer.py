#!/usr/bin/env python3
"""
AWS Cost Optimization Analyzer

Fetches and analyzes AWS cost data using Cost Explorer API.
Identifies savings opportunities and generates reports.
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict


class CostAnalyzer:
    """Analyzes AWS costs and identifies optimization opportunities."""

    def __init__(self, region='us-east-1'):
        """Initialize AWS clients."""
        self.ce = boto3.client('ce', region_name=region)
        self.ec2 = boto3.client('ec2', region_name=region)
        self.rds = boto3.client('rds', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)

    def get_cost_by_service(self, days=30) -> Dict:
        """
        Get cost breakdown by service.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with service costs
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        costs = {}
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                costs[service] = costs.get(service, 0) + cost

        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True))

    def get_cost_trend(self, days=90) -> List[Dict]:
        """
        Get daily cost trend.

        Args:
            days: Number of days to analyze

        Returns:
            List of daily cost data
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )

        trends = []
        for result in response['ResultsByTime']:
            trends.append({
                'date': result['TimePeriod']['Start'],
                'cost': float(result['Total']['UnblendedCost']['Amount'])
            })

        return trends

    def identify_idle_resources(self) -> Dict[str, List]:
        """
        Identify idle resources that may be wasting money.

        Returns:
            Dictionary of idle resources by type
        """
        idle_resources = defaultdict(list)

        # Check for stopped EC2 instances (still incurring EBS costs)
        ec2_response = self.ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        )

        for reservation in ec2_response['Reservations']:
            for instance in reservation['Instances']:
                idle_resources['stopped_ec2'].append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType'],
                    'launch_time': instance['LaunchTime'].isoformat(),
                    'recommendation': 'Terminate if no longer needed, or start to utilize'
                })

        # Check for unattached EBS volumes
        volumes = self.ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )

        for volume in volumes['Volumes']:
            idle_resources['unattached_ebs'].append({
                'id': volume['VolumeId'],
                'size': volume['Size'],
                'type': volume['VolumeType'],
                'created': volume['CreateTime'].isoformat(),
                'recommendation': 'Delete if no longer needed, or create snapshot and delete'
            })

        # Check for old EBS snapshots (>90 days)
        snapshots = self.ec2.describe_snapshots(OwnerIds=['self'])
        ninety_days_ago = datetime.now() - timedelta(days=90)

        for snapshot in snapshots['Snapshots']:
            if snapshot['StartTime'].replace(tzinfo=None) < ninety_days_ago:
                idle_resources['old_snapshots'].append({
                    'id': snapshot['SnapshotId'],
                    'size': snapshot['VolumeSize'],
                    'created': snapshot['StartTime'].isoformat(),
                    'recommendation': 'Archive to Glacier or delete if no longer needed'
                })

        # Check for idle RDS instances (low CPU)
        try:
            rds_instances = self.rds.describe_db_instances()
            cloudwatch = boto3.client('cloudwatch')

            for db in rds_instances['DBInstances']:
                # Get CPU metrics for last 7 days
                metrics = cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='CPUUtilization',
                    Dimensions=[
                        {'Name': 'DBInstanceIdentifier', 'Value': db['DBInstanceIdentifier']}
                    ],
                    StartTime=datetime.now() - timedelta(days=7),
                    EndTime=datetime.now(),
                    Period=3600,
                    Statistics=['Average']
                )

                if metrics['Datapoints']:
                    avg_cpu = sum(d['Average'] for d in metrics['Datapoints']) / len(metrics['Datapoints'])
                    if avg_cpu < 10:  # Less than 10% CPU usage
                        idle_resources['underutilized_rds'].append({
                            'id': db['DBInstanceIdentifier'],
                            'class': db['DBInstanceClass'],
                            'engine': db['Engine'],
                            'avg_cpu': f"{avg_cpu:.2f}%",
                            'recommendation': 'Consider downsizing instance class or using Aurora Serverless'
                        })
        except Exception as e:
            print(f"Warning: Could not analyze RDS instances: {e}")

        return dict(idle_resources)

    def get_reserved_instance_recommendations(self) -> List[Dict]:
        """
        Get Reserved Instance purchase recommendations.

        Returns:
            List of RI recommendations
        """
        try:
            response = self.ce.get_reservation_purchase_recommendation(
                Service='Amazon Elastic Compute Cloud - Compute',
                LookbackPeriodInDays='SIXTY_DAYS',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )

            recommendations = []
            for recommendation in response.get('Recommendations', []):
                details = recommendation['RecommendationDetails'][0]
                recommendations.append({
                    'instance_type': details['InstanceDetails']['EC2InstanceDetails']['InstanceType'],
                    'region': details['InstanceDetails']['EC2InstanceDetails']['Region'],
                    'estimated_monthly_savings': details['EstimatedMonthlySavingsAmount'],
                    'estimated_monthly_on_demand_cost': details['EstimatedMonthlyOnDemandCost'],
                    'recommended_instances': details['RecommendedNumberOfInstancesToPurchase']
                })

            return recommendations
        except Exception as e:
            print(f"Warning: Could not get RI recommendations: {e}")
            return []

    def generate_report(self, output_file='cost_report.json'):
        """
        Generate comprehensive cost optimization report.

        Args:
            output_file: Path to output JSON file
        """
        print("Generating cost optimization report...")

        report = {
            'generated_at': datetime.now().isoformat(),
            'cost_by_service': self.get_cost_by_service(30),
            'cost_trend_30_days': self.get_cost_trend(30)[-30:],
            'idle_resources': self.identify_idle_resources(),
            'ri_recommendations': self.get_reserved_instance_recommendations(),
            'summary': {}
        }

        # Calculate summary
        total_cost = sum(report['cost_by_service'].values())
        total_idle = sum(
            len(resources)
            for resources in report['idle_resources'].values()
        )

        report['summary'] = {
            'total_monthly_cost': f"${total_cost:.2f}",
            'top_3_services': list(report['cost_by_service'].keys())[:3],
            'idle_resources_count': total_idle,
            'potential_savings': 'See RI recommendations'
        }

        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"Report saved to: {output_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("COST OPTIMIZATION REPORT SUMMARY")
        print("=" * 60)
        print(f"Total Monthly Cost: {report['summary']['total_monthly_cost']}")
        print(f"\nTop 3 Services:")
        for i, service in enumerate(report['summary']['top_3_services'], 1):
            cost = report['cost_by_service'][service]
            print(f"  {i}. {service}: ${cost:.2f}")

        print(f"\nIdle Resources Found: {total_idle}")
        for resource_type, resources in report['idle_resources'].items():
            print(f"  - {resource_type}: {len(resources)}")

        if report['ri_recommendations']:
            print(f"\nRI Recommendations: {len(report['ri_recommendations'])} opportunities")

        return report


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='AWS Cost Optimization Analyzer')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--output', default='cost_report.json', help='Output file')
    parser.add_argument('--days', type=int, default=30, help='Days to analyze')

    args = parser.parse_args()

    analyzer = CostAnalyzer(region=args.region)
    analyzer.generate_report(output_file=args.output)


if __name__ == '__main__':
    main()
