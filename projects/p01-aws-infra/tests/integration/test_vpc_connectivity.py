"""
Integration tests for VPC connectivity and networking.

These tests verify that VPC components are correctly configured and accessible.
"""

import boto3
import pytest
import os
from typing import List, Dict

# Test configuration
STACK_NAME = os.getenv('STACK_NAME', 'p01-test-stack')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')


@pytest.fixture(scope='module')
def aws_clients():
    """Create AWS service clients."""
    return {
        'ec2': boto3.client('ec2', region_name=AWS_REGION),
        'cfn': boto3.client('cloudformation', region_name=AWS_REGION),
        'rds': boto3.client('rds', region_name=AWS_REGION)
    }


@pytest.fixture(scope='module')
def stack_outputs(aws_clients) -> Dict[str, str]:
    """Get CloudFormation stack outputs."""
    response = aws_clients['cfn'].describe_stacks(StackName=STACK_NAME)
    outputs = response['Stacks'][0].get('Outputs', [])
    return {output['OutputKey']: output['OutputValue'] for output in outputs}


class TestVPCConfiguration:
    """Test VPC configuration and components."""

    def test_vpc_exists(self, aws_clients, stack_outputs):
        """Verify VPC exists and has correct CIDR block."""
        vpc_id = stack_outputs.get('VPCId')
        assert vpc_id is not None, "VPC ID not found in stack outputs"

        response = aws_clients['ec2'].describe_vpcs(VpcIds=[vpc_id])
        assert len(response['Vpcs']) == 1

        vpc = response['Vpcs'][0]
        assert vpc['State'] == 'available'
        assert vpc['CidrBlock'] == '10.0.0.0/16'

    def test_vpc_dns_settings(self, aws_clients, stack_outputs):
        """Verify VPC has DNS hostname and DNS support enabled."""
        vpc_id = stack_outputs.get('VPCId')

        response = aws_clients['ec2'].describe_vpc_attribute(
            VpcId=vpc_id,
            Attribute='enableDnsHostnames'
        )
        assert response['EnableDnsHostnames']['Value'] is True

        response = aws_clients['ec2'].describe_vpc_attribute(
            VpcId=vpc_id,
            Attribute='enableDnsSupport'
        )
        assert response['EnableDnsSupport']['Value'] is True

    def test_subnets_exist_in_three_azs(self, aws_clients, stack_outputs):
        """Verify public and private subnets exist across 3 AZs."""
        vpc_id = stack_outputs.get('VPCId')

        response = aws_clients['ec2'].describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        subnets = response['Subnets']

        # Should have 6 subnets (3 public + 3 private)
        assert len(subnets) >= 6, f"Expected at least 6 subnets, found {len(subnets)}"

        # Check availability zones
        azs = set(subnet['AvailabilityZone'] for subnet in subnets)
        assert len(azs) == 3, f"Expected 3 AZs, found {len(azs)}"

    def test_public_subnets_tagged_correctly(self, aws_clients, stack_outputs):
        """Verify public subnets have correct tags."""
        vpc_id = stack_outputs.get('VPCId')

        response = aws_clients['ec2'].describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Tier', 'Values': ['Public']}
            ]
        )
        public_subnets = response['Subnets']

        assert len(public_subnets) == 3, f"Expected 3 public subnets, found {len(public_subnets)}"

        # Verify public subnets have MapPublicIpOnLaunch enabled
        for subnet in public_subnets:
            assert subnet['MapPublicIpOnLaunch'] is True

    def test_private_subnets_tagged_correctly(self, aws_clients, stack_outputs):
        """Verify private subnets have correct tags."""
        vpc_id = stack_outputs.get('VPCId')

        response = aws_clients['ec2'].describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Tier', 'Values': ['Private']}
            ]
        )
        private_subnets = response['Subnets']

        assert len(private_subnets) == 3, f"Expected 3 private subnets, found {len(private_subnets)}"

        # Verify private subnets do NOT have MapPublicIpOnLaunch enabled
        for subnet in private_subnets:
            assert subnet['MapPublicIpOnLaunch'] is False


class TestInternetGateway:
    """Test Internet Gateway configuration."""

    def test_internet_gateway_attached(self, aws_clients, stack_outputs):
        """Verify Internet Gateway is attached to VPC."""
        vpc_id = stack_outputs.get('VPCId')

        response = aws_clients['ec2'].describe_internet_gateways(
            Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
        )

        assert len(response['InternetGateways']) >= 1
        igw = response['InternetGateways'][0]

        attachments = igw['Attachments']
        assert len(attachments) == 1
        assert attachments[0]['State'] == 'available'
        assert attachments[0]['VpcId'] == vpc_id


class TestNATGateways:
    """Test NAT Gateway configuration."""

    def test_nat_gateways_exist(self, aws_clients, stack_outputs):
        """Verify NAT Gateways exist and are available."""
        vpc_id = stack_outputs.get('VPCId')

        # Get public subnets
        response = aws_clients['ec2'].describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Tier', 'Values': ['Public']}
            ]
        )
        public_subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]

        # Check NAT Gateways
        response = aws_clients['ec2'].describe_nat_gateways(
            Filters=[{'Name': 'subnet-id', 'Values': public_subnet_ids}]
        )
        nat_gateways = response['NatGateways']

        # Should have at least 1 NAT Gateway (could be 3 for HA)
        assert len(nat_gateways) >= 1, f"Expected at least 1 NAT Gateway, found {len(nat_gateways)}"

        # Verify all NAT Gateways are available
        for nat_gw in nat_gateways:
            assert nat_gw['State'] in ['available', 'pending']

    def test_nat_gateways_have_elastic_ips(self, aws_clients, stack_outputs):
        """Verify NAT Gateways have Elastic IPs assigned."""
        vpc_id = stack_outputs.get('VPCId')

        # Get NAT Gateways
        response = aws_clients['ec2'].describe_nat_gateways(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        nat_gateways = response['NatGateways']

        for nat_gw in nat_gateways:
            nat_addresses = nat_gw.get('NatGatewayAddresses', [])
            assert len(nat_addresses) >= 1, f"NAT Gateway {nat_gw['NatGatewayId']} has no Elastic IP"

            for addr in nat_addresses:
                assert addr.get('PublicIp') is not None


class TestRouteTables:
    """Test route table configuration."""

    def test_public_route_to_internet_gateway(self, aws_clients, stack_outputs):
        """Verify public subnets have routes to Internet Gateway."""
        vpc_id = stack_outputs.get('VPCId')

        # Get public subnets
        response = aws_clients['ec2'].describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Tier', 'Values': ['Public']}
            ]
        )
        public_subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]

        # Check route tables for public subnets
        for subnet_id in public_subnet_ids:
            response = aws_clients['ec2'].describe_route_tables(
                Filters=[{'Name': 'association.subnet-id', 'Values': [subnet_id]}]
            )

            assert len(response['RouteTables']) >= 1
            route_table = response['RouteTables'][0]

            # Verify route to Internet Gateway exists
            routes = route_table['Routes']
            igw_route = next(
                (r for r in routes if r.get('GatewayId', '').startswith('igw-')),
                None
            )
            assert igw_route is not None, f"No IGW route found for subnet {subnet_id}"
            assert igw_route['DestinationCidrBlock'] == '0.0.0.0/0'

    def test_private_route_to_nat_gateway(self, aws_clients, stack_outputs):
        """Verify private subnets have routes to NAT Gateway."""
        vpc_id = stack_outputs.get('VPCId')

        # Get private subnets
        response = aws_clients['ec2'].describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Tier', 'Values': ['Private']}
            ]
        )
        private_subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]

        # Check route tables for private subnets
        for subnet_id in private_subnet_ids:
            response = aws_clients['ec2'].describe_route_tables(
                Filters=[{'Name': 'association.subnet-id', 'Values': [subnet_id]}]
            )

            if len(response['RouteTables']) == 0:
                # Subnet might be using main route table
                continue

            route_table = response['RouteTables'][0]

            # Verify route to NAT Gateway exists
            routes = route_table['Routes']
            nat_route = next(
                (r for r in routes if r.get('NatGatewayId', '').startswith('nat-')),
                None
            )
            assert nat_route is not None, f"No NAT route found for subnet {subnet_id}"
            assert nat_route['DestinationCidrBlock'] == '0.0.0.0/0'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
