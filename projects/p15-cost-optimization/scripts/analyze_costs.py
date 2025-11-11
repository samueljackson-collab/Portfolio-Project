#!/usr/bin/env python3
"""
AWS Cost Analysis Script
Analyzes AWS costs using Cost Explorer API and provides optimization recommendations
"""
import boto3
import json
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import sys


class CostAnalyzer:
    def __init__(self, region='us-east-1'):
        self.ce_client = boto3.client('ce', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.rds_client = boto3.client('rds', region_name=region)

    def get_cost_and_usage(self, start_date, end_date, granularity='MONTHLY'):
        """Fetch cost and usage data from Cost Explorer"""
        response = self.ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Metrics=['UnblendedCost', 'UsageQuantity'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            ]
        )
        return response

    def get_cost_by_service(self, days=30):
        """Get cost breakdown by service"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        response = self.get_cost_and_usage(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        costs = defaultdict(float)
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                costs[service] += amount

        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True))

    def get_cost_forecast(self, days=30):
        """Get cost forecast for the next N days"""
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days)

        response = self.ce_client.get_cost_forecast(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Metric='UNBLENDED_COST',
            Granularity='MONTHLY'
        )

        return {
            'amount': float(response['Total']['Amount']),
            'unit': response['Total']['Unit']
        }

    def identify_idle_ec2_instances(self):
        """Identify potentially idle EC2 instances"""
        instances = []
        response = self.ec2_client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_data = {
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'LaunchTime': instance['LaunchTime'].isoformat(),
                    'State': instance['State']['Name']
                }
                instances.append(instance_data)

        return instances

    def identify_unattached_volumes(self):
        """Identify unattached EBS volumes"""
        volumes = []
        response = self.ec2_client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )

        for volume in response['Volumes']:
            volume_data = {
                'VolumeId': volume['VolumeId'],
                'Size': volume['Size'],
                'VolumeType': volume['VolumeType'],
                'CreateTime': volume['CreateTime'].isoformat(),
                'State': volume['State']
            }
            volumes.append(volume_data)

        return volumes

    def identify_idle_rds_instances(self):
        """Identify potentially idle RDS instances"""
        instances = []
        response = self.rds_client.describe_db_instances()

        for db_instance in response['DBInstances']:
            instance_data = {
                'DBInstanceIdentifier': db_instance['DBInstanceIdentifier'],
                'DBInstanceClass': db_instance['DBInstanceClass'],
                'Engine': db_instance['Engine'],
                'DBInstanceStatus': db_instance['DBInstanceStatus'],
                'AllocatedStorage': db_instance['AllocatedStorage']
            }
            instances.append(instance_data)

        return instances

    def get_rightsizing_recommendations(self):
        """Get EC2 rightsizing recommendations"""
        response = self.ce_client.get_rightsizing_recommendation(
            Service='AmazonEC2',
            Configuration={
                'RecommendationTarget': 'SAME_INSTANCE_FAMILY',
                'BenefitsConsidered': True
            }
        )

        recommendations = []
        for rec in response.get('RightsizingRecommendations', []):
            recommendations.append({
                'AccountId': rec.get('AccountId'),
                'CurrentInstance': rec['CurrentInstance']['ResourceDetails']['EC2ResourceDetails']['InstanceType'],
                'RecommendedInstance': rec['ModifyRecommendationDetail']['TargetInstances'][0]['ResourceDetails']['EC2ResourceDetails']['InstanceType'] if rec.get('ModifyRecommendationDetail') else None,
                'EstimatedMonthlySavings': float(rec['ModifyRecommendationDetail']['TargetInstances'][0]['EstimatedMonthlySavings']) if rec.get('ModifyRecommendationDetail') else 0
            })

        return recommendations

    def generate_report(self):
        """Generate comprehensive cost analysis report"""
        print("=" * 80)
        print("AWS COST ANALYSIS REPORT")
        print("Generated:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("=" * 80)
        print()

        # Cost by Service
        print("1. COST BY SERVICE (Last 30 Days)")
        print("-" * 80)
        costs = self.get_cost_by_service(30)
        total_cost = sum(costs.values())

        for service, cost in list(costs.items())[:10]:
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            print(f"  {service:<40} ${cost:>10.2f}  ({percentage:>5.1f}%)")

        print(f"\n  {'TOTAL':<40} ${total_cost:>10.2f}")
        print()

        # Cost Forecast
        print("2. COST FORECAST (Next 30 Days)")
        print("-" * 80)
        forecast = self.get_cost_forecast(30)
        print(f"  Estimated cost: ${forecast['amount']:.2f} {forecast['unit']}")
        print()

        # Idle Resources
        print("3. OPTIMIZATION OPPORTUNITIES")
        print("-" * 80)

        # Unattached volumes
        volumes = self.identify_unattached_volumes()
        if volumes:
            print(f"\n  Unattached EBS Volumes: {len(volumes)}")
            total_size = sum(v['Size'] for v in volumes)
            estimated_cost = total_size * 0.10  # Rough estimate: $0.10/GB/month
            print(f"    Total Size: {total_size} GB")
            print(f"    Estimated Monthly Cost: ${estimated_cost:.2f}")

            for vol in volumes[:5]:
                print(f"      - {vol['VolumeId']}: {vol['Size']} GB ({vol['VolumeType']})")
            if len(volumes) > 5:
                print(f"      ... and {len(volumes) - 5} more")

        # Running EC2 instances
        instances = self.identify_idle_ec2_instances()
        if instances:
            print(f"\n  Running EC2 Instances: {len(instances)}")
            print("    Review for idle instances and potential rightsizing")

        # RDS instances
        rds_instances = self.identify_idle_rds_instances()
        if rds_instances:
            print(f"\n  Active RDS Instances: {len(rds_instances)}")
            for db in rds_instances[:3]:
                print(f"      - {db['DBInstanceIdentifier']}: {db['DBInstanceClass']} ({db['Engine']})")

        # Rightsizing recommendations
        try:
            recommendations = self.get_rightsizing_recommendations()
            if recommendations:
                print(f"\n  Rightsizing Recommendations: {len(recommendations)}")
                total_savings = sum(r['EstimatedMonthlySavings'] for r in recommendations)
                print(f"    Total Potential Monthly Savings: ${total_savings:.2f}")

                for rec in recommendations[:5]:
                    if rec['RecommendedInstance']:
                        print(f"      - {rec['CurrentInstance']} → {rec['RecommendedInstance']}: ${rec['EstimatedMonthlySavings']:.2f}/month")
        except Exception as e:
            print(f"\n  Rightsizing Recommendations: Not available ({str(e)})")

        print()
        print("=" * 80)
        print("END OF REPORT")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description='Analyze AWS costs and provide recommendations')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    args = parser.parse_args()

    analyzer = CostAnalyzer(region=args.region)

    if args.json:
        report = {
            'generated_at': datetime.now().isoformat(),
            'costs_by_service': analyzer.get_cost_by_service(30),
            'forecast': analyzer.get_cost_forecast(30),
            'unattached_volumes': analyzer.identify_unattached_volumes(),
            'running_ec2_instances': analyzer.identify_idle_ec2_instances(),
            'rds_instances': analyzer.identify_idle_rds_instances()
        }
        print(json.dumps(report, indent=2, default=str))
    else:
        analyzer.generate_report()


if __name__ == '__main__':
    main()
