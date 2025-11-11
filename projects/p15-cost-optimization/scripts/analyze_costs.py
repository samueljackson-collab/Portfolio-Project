#!/usr/bin/env python3
"""
AWS Cost Analysis and Optimization Recommendations
Analyzes actual AWS costs and provides actionable recommendations
"""
import sys
import boto3
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple

class AWSCostAnalyzer:
    """Analyzes AWS costs and generates optimization recommendations."""

    def __init__(self):
        """Initialize AWS Cost Explorer client."""
        try:
            self.ce_client = boto3.client('ce')  # Cost Explorer
            self.ec2_client = boto3.client('ec2')
            self.s3_client = boto3.client('s3')
            self.rds_client = boto3.client('rds')
            print("✓ Connected to AWS Cost Explorer API")
        except Exception as e:
            print(f"⚠ Warning: Could not connect to AWS: {e}")
            print("  Running in demo mode with sample data")
            self.ce_client = None

    def get_cost_data(self, days_back: int = 30) -> Dict:
        """Fetch cost data from AWS Cost Explorer."""
        if not self.ce_client:
            return self._get_sample_cost_data()

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        try:
            # Get cost and usage data grouped by service
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                ]
            )

            # Parse cost data by service
            cost_by_service = {}
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    if service not in cost_by_service:
                        cost_by_service[service] = 0
                    cost_by_service[service] += cost

            return {
                'total_cost': sum(cost_by_service.values()),
                'by_service': cost_by_service,
                'period_days': days_back
            }

        except Exception as e:
            print(f"⚠ Error fetching cost data: {e}")
            return self._get_sample_cost_data()

    def _get_sample_cost_data(self) -> Dict:
        """Return sample cost data for demonstration."""
        return {
            'total_cost': 1247.35,
            'by_service': {
                'Amazon Elastic Compute Cloud - Compute': 485.20,
                'Amazon Relational Database Service': 312.50,
                'Amazon Simple Storage Service': 128.45,
                'AWS Data Transfer': 98.70,
                'Amazon Elastic Load Balancing': 75.30,
                'Amazon CloudWatch': 42.15,
                'AWS Lambda': 38.25,
                'Amazon Elastic Block Store': 66.80
            },
            'period_days': 30,
            'demo_mode': True
        }

    def analyze_ec2_idle_resources(self) -> List[Dict]:
        """Identify idle or underutilized EC2 instances."""
        idle_resources = []

        if not self.ec2_client:
            return [{
                'resource_type': 'EC2 Instance',
                'resource_id': 'i-0123456789abcdef0',
                'status': 'stopped',
                'estimated_savings': '$45/month',
                'recommendation': 'Terminate or convert to Reserved Instance'
            }]

        try:
            # Find stopped instances
            response = self.ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
            )

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    idle_resources.append({
                        'resource_type': 'EC2 Instance',
                        'resource_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'status': 'stopped',
                        'launch_time': instance['LaunchTime'].strftime('%Y-%m-%d'),
                        'recommendation': 'Terminate if no longer needed or start if required'
                    })

            # Find unattached EBS volumes
            volumes = self.ec2_client.describe_volumes(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )

            for volume in volumes['Volumes']:
                size_gb = volume['Size']
                estimated_cost = size_gb * 0.10  # ~$0.10/GB/month for gp3
                idle_resources.append({
                    'resource_type': 'EBS Volume',
                    'resource_id': volume['VolumeId'],
                    'size_gb': size_gb,
                    'status': 'unattached',
                    'estimated_savings': f'${estimated_cost:.2f}/month',
                    'recommendation': 'Delete if no longer needed or create snapshot and delete'
                })

        except Exception as e:
            print(f"  ⚠ Could not analyze EC2 resources: {e}")

        return idle_resources

    def analyze_s3_storage(self) -> List[Dict]:
        """Analyze S3 storage for optimization opportunities."""
        s3_recommendations = []

        if not self.s3_client:
            return [{
                'bucket': 'example-logs-bucket',
                'size_gb': 450,
                'storage_class': 'STANDARD',
                'recommendation': 'Enable Intelligent-Tiering',
                'estimated_savings': '$90/month'
            }]

        try:
            buckets = self.s3_client.list_buckets()

            for bucket in buckets['Buckets']:
                bucket_name = bucket['Name']

                # Check lifecycle policies
                try:
                    self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                    has_lifecycle = True
                except:
                    has_lifecycle = False

                # Check versioning
                try:
                    versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                    is_versioned = versioning.get('Status') == 'Enabled'
                except:
                    is_versioned = False

                if not has_lifecycle:
                    s3_recommendations.append({
                        'bucket': bucket_name,
                        'issue': 'No lifecycle policy',
                        'recommendation': 'Implement lifecycle policy to transition old objects to cheaper storage tiers',
                        'potential_savings': 'Up to 50-80% on old data'
                    })

                if is_versioned:
                    s3_recommendations.append({
                        'bucket': bucket_name,
                        'issue': 'Versioning enabled',
                        'recommendation': 'Add lifecycle rule to delete old versions or transition to Glacier',
                        'potential_savings': 'Significant if many versions accumulate'
                    })

        except Exception as e:
            print(f"  ⚠ Could not analyze S3 buckets: {e}")

        return s3_recommendations

    def generate_recommendations(self, cost_data: Dict) -> List[str]:
        """Generate personalized recommendations based on cost data."""
        recommendations = []
        by_service = cost_data['by_service']
        total = cost_data['total_cost']

        # EC2-specific recommendations
        ec2_cost = by_service.get('Amazon Elastic Compute Cloud - Compute', 0)
        if ec2_cost > total * 0.3:  # More than 30% of total
            ec2_percent = (ec2_cost / total * 100)
            recommendations.append({
                'priority': 'HIGH',
                'category': 'EC2',
                'issue': f'EC2 costs are {ec2_percent:.1f}% of total (${ec2_cost:.2f})',
                'recommendation': 'Consider Reserved Instances or Savings Plans for steady-state workloads',
                'potential_savings': 'Up to 72% with 3-year commitments, 40% with 1-year'
            })
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'EC2',
                'recommendation': 'Evaluate Spot Instances for fault-tolerant workloads (batch processing, CI/CD)',
                'potential_savings': 'Up to 90% vs On-Demand pricing'
            })

        # RDS-specific recommendations
        rds_cost = by_service.get('Amazon Relational Database Service', 0)
        if rds_cost > 200:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'RDS',
                'issue': f'RDS costs are significant (${rds_cost:.2f}/month)',
                'recommendation': 'Consider RDS Reserved Instances for production databases',
                'potential_savings': 'Up to 60% with multi-year commitments'
            })
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'RDS',
                'recommendation': 'Review instance sizes - right-size based on CloudWatch metrics',
                'potential_savings': '20-40% by downsizing oversized instances'
            })

        # S3-specific recommendations
        s3_cost = by_service.get('Amazon Simple Storage Service', 0)
        if s3_cost > 50:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'S3',
                'issue': f'S3 costs: ${s3_cost:.2f}/month',
                'recommendation': 'Enable S3 Intelligent-Tiering for data with unknown access patterns',
                'potential_savings': 'Up to 70% on infrequently accessed data'
            })
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'S3',
                'recommendation': 'Implement lifecycle policies to move old data to Glacier/Deep Archive',
                'potential_savings': 'Up to 95% on archival storage'
            })

        # Data transfer recommendations
        transfer_cost = by_service.get('AWS Data Transfer', 0)
        if transfer_cost > 50:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Networking',
                'issue': f'Data transfer costs are high (${transfer_cost:.2f})',
                'recommendation': 'Use CloudFront for static content, VPC endpoints for AWS service access',
                'potential_savings': '30-50% reduction in data transfer costs'
            })

        # General recommendations
        recommendations.append({
            'priority': 'LOW',
            'category': 'Monitoring',
            'recommendation': 'Set up AWS Budgets with alerts at 50%, 80%, and 100% of forecast',
            'potential_savings': 'Prevent overspending and catch anomalies early'
        })

        recommendations.append({
            'priority': 'LOW',
            'category': 'Tagging',
            'recommendation': 'Implement comprehensive resource tagging for cost allocation',
            'potential_savings': 'Better visibility enables 10-20% cost reduction through accountability'
        })

        return recommendations

    def print_cost_summary(self, cost_data: Dict):
        """Print formatted cost summary."""
        print("\n" + "="*70)
        print("AWS COST ANALYSIS SUMMARY")
        print("="*70)

        if cost_data.get('demo_mode'):
            print("⚠ Running in DEMO MODE - using sample data (AWS credentials not configured)")
            print()

        print(f"Analysis Period: Last {cost_data['period_days']} days")
        print(f"Total Cost: ${cost_data['total_cost']:.2f}")
        print("\nCost Breakdown by Service:")
        print("-" * 70)

        # Sort services by cost
        sorted_services = sorted(
            cost_data['by_service'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        for service, cost in sorted_services:
            percent = (cost / cost_data['total_cost'] * 100)
            print(f"  {service[:50]:<50} ${cost:>8.2f} ({percent:>5.1f}%)")

    def print_recommendations(self, recommendations: List[Dict]):
        """Print formatted recommendations."""
        print("\n" + "="*70)
        print("COST OPTIMIZATION RECOMMENDATIONS")
        print("="*70)

        # Group by priority
        by_priority = defaultdict(list)
        for rec in recommendations:
            by_priority[rec.get('priority', 'LOW')].append(rec)

        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            if priority in by_priority:
                print(f"\n{priority} PRIORITY:")
                print("-" * 70)

                for i, rec in enumerate(by_priority[priority], 1):
                    category = rec.get('category', 'General')
                    print(f"\n{i}. [{category}] {rec['recommendation']}")

                    if 'issue' in rec:
                        print(f"   Issue: {rec['issue']}")

                    if 'potential_savings' in rec:
                        print(f"   💰 Potential Savings: {rec['potential_savings']}")

    def run_analysis(self) -> int:
        """Run complete cost analysis."""
        print("Starting AWS Cost Analysis...")
        print()

        # Get cost data
        cost_data = self.get_cost_data(days_back=30)

        # Print cost summary
        self.print_cost_summary(cost_data)

        # Generate and print recommendations
        recommendations = self.generate_recommendations(cost_data)
        self.print_recommendations(recommendations)

        # Analyze idle resources
        print("\n" + "="*70)
        print("IDLE RESOURCE ANALYSIS")
        print("="*70)
        idle_resources = self.analyze_ec2_idle_resources()

        if idle_resources:
            print(f"\nFound {len(idle_resources)} idle or underutilized resources:")
            for resource in idle_resources[:10]:  # Limit to 10
                print(f"\n  • {resource['resource_type']}: {resource['resource_id']}")
                if 'instance_type' in resource:
                    print(f"    Type: {resource['instance_type']}")
                if 'size_gb' in resource:
                    print(f"    Size: {resource['size_gb']} GB")
                print(f"    Status: {resource['status']}")
                if 'estimated_savings' in resource:
                    print(f"    💰 Estimated Savings: {resource['estimated_savings']}")
                print(f"    ✓ Action: {resource['recommendation']}")
        else:
            print("\n✓ No idle resources found")

        # Analyze S3 storage
        print("\n" + "="*70)
        print("S3 STORAGE OPTIMIZATION")
        print("="*70)
        s3_recs = self.analyze_s3_storage()

        if s3_recs:
            print(f"\nFound {len(s3_recs)} S3 optimization opportunities:")
            for rec in s3_recs[:10]:
                print(f"\n  • Bucket: {rec['bucket']}")
                if 'issue' in rec:
                    print(f"    Issue: {rec['issue']}")
                print(f"    ✓ Recommendation: {rec['recommendation']}")
                if 'potential_savings' in rec:
                    print(f"    💰 Potential Savings: {rec['potential_savings']}")
        else:
            print("\n✓ All S3 buckets appear optimized")

        print("\n" + "="*70)
        print("✓ Cost analysis completed successfully")
        print("="*70)

        return 0


def main():
    """Main entry point."""
    analyzer = AWSCostAnalyzer()
    return analyzer.run_analysis()


if __name__ == "__main__":
    sys.exit(main())
