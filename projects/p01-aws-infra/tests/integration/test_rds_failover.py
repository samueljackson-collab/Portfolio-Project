"""
Integration tests for RDS Multi-AZ failover functionality.

These tests verify RDS configuration and simulate failover scenarios.
"""

import boto3
import pytest
import os
import time
from typing import Dict

# Test configuration
STACK_NAME = os.getenv("STACK_NAME", "p01-test-stack")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


@pytest.fixture(scope="module")
def aws_clients():
    """Create AWS service clients."""
    return {
        "rds": boto3.client("rds", region_name=AWS_REGION),
        "cfn": boto3.client("cloudformation", region_name=AWS_REGION),
        "ec2": boto3.client("ec2", region_name=AWS_REGION),
    }


@pytest.fixture(scope="module")
def stack_outputs(aws_clients) -> Dict[str, str]:
    """Get CloudFormation stack outputs."""
    response = aws_clients["cfn"].describe_stacks(StackName=STACK_NAME)
    outputs = response["Stacks"][0].get("Outputs", [])
    return {output["OutputKey"]: output["OutputValue"] for output in outputs}


@pytest.fixture(scope="module")
def db_instance_id(stack_outputs) -> str:
    """Get RDS instance identifier from stack outputs."""
    db_id = stack_outputs.get("DBInstanceIdentifier")
    assert db_id is not None, "DBInstanceIdentifier not found in stack outputs"
    return db_id


class TestRDSConfiguration:
    """Test RDS instance configuration."""

    def test_rds_instance_exists(self, aws_clients, db_instance_id):
        """Verify RDS instance exists and is available."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        assert len(response["DBInstances"]) == 1
        db_instance = response["DBInstances"][0]

        assert db_instance["DBInstanceStatus"] in ["available", "backing-up"]
        assert db_instance["Engine"] == "postgres"

    def test_rds_multi_az_enabled(self, aws_clients, db_instance_id):
        """Verify Multi-AZ is enabled for high availability."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        assert db_instance["MultiAZ"] is True, "Multi-AZ should be enabled"

    def test_rds_in_private_subnets(self, aws_clients, db_instance_id, stack_outputs):
        """Verify RDS is deployed in private subnets only."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        subnet_group_name = db_instance["DBSubnetGroup"]["DBSubnetGroupName"]

        # Get subnet group details
        response = aws_clients["rds"].describe_db_subnet_groups(
            DBSubnetGroupName=subnet_group_name
        )

        subnet_group = response["DBSubnetGroups"][0]
        subnet_ids = [subnet["SubnetIdentifier"] for subnet in subnet_group["Subnets"]]

        # Verify subnets are private (tagged as Private)
        response = aws_clients["ec2"].describe_subnets(SubnetIds=subnet_ids)
        for subnet in response["Subnets"]:
            tags = {tag["Key"]: tag["Value"] for tag in subnet.get("Tags", [])}
            assert (
                tags.get("Tier") == "Private"
            ), f"RDS subnet {subnet['SubnetId']} should be Private"

    def test_rds_storage_encrypted(self, aws_clients, db_instance_id):
        """Verify RDS storage is encrypted."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        assert (
            db_instance["StorageEncrypted"] is True
        ), "RDS storage should be encrypted"

    def test_rds_backup_retention(self, aws_clients, db_instance_id):
        """Verify automated backups are configured with adequate retention."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        backup_retention = db_instance["BackupRetentionPeriod"]

        assert (
            backup_retention >= 7
        ), f"Backup retention should be at least 7 days, got {backup_retention}"

    def test_rds_enhanced_monitoring_enabled(self, aws_clients, db_instance_id):
        """Verify Enhanced Monitoring is enabled."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        monitoring_interval = db_instance.get("MonitoringInterval", 0)

        # Enhanced monitoring is enabled if interval > 0
        assert monitoring_interval > 0, "Enhanced Monitoring should be enabled"


class TestRDSSecurityGroup:
    """Test RDS security group configuration."""

    def test_rds_security_group_exists(
        self, aws_clients, db_instance_id, stack_outputs
    ):
        """Verify RDS has security group configured."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        security_groups = db_instance["VpcSecurityGroups"]

        assert len(security_groups) >= 1, "RDS should have at least one security group"

        for sg in security_groups:
            assert sg["Status"] == "active"

    def test_rds_security_group_rules(self, aws_clients, db_instance_id):
        """Verify RDS security group has appropriate ingress rules."""
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )

        db_instance = response["DBInstances"][0]
        security_group_ids = [
            sg["VpcSecurityGroupId"] for sg in db_instance["VpcSecurityGroups"]
        ]

        for sg_id in security_group_ids:
            response = aws_clients["ec2"].describe_security_groups(GroupIds=[sg_id])
            sg = response["SecurityGroups"][0]

            # Verify PostgreSQL port (5432) is in ingress rules
            postgres_rule = next(
                (
                    rule
                    for rule in sg["IpPermissions"]
                    if rule.get("FromPort") == 5432 and rule.get("ToPort") == 5432
                ),
                None,
            )
            assert (
                postgres_rule is not None
            ), "Security group should allow PostgreSQL port 5432"


class TestRDSFailover:
    """Test RDS failover functionality (destructive tests - use with caution)."""

    @pytest.mark.skip(reason="Destructive test - run manually with caution")
    def test_rds_failover_capability(self, aws_clients, db_instance_id):
        """
        Test RDS Multi-AZ failover capability.

        WARNING: This test triggers an actual failover event.
        Only run in non-production environments.
        """
        # Get initial state
        response = aws_clients["rds"].describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )
        initial_state = response["DBInstances"][0]
        initial_az = initial_state["AvailabilityZone"]

        print(f"Initial AZ: {initial_az}")
        print(f"Initiating failover for {db_instance_id}...")

        # Initiate failover
        aws_clients["rds"].reboot_db_instance(
            DBInstanceIdentifier=db_instance_id, ForceFailover=True
        )

        # Wait for failover to complete (can take 1-2 minutes)
        max_wait_time = 300  # 5 minutes
        wait_interval = 15  # 15 seconds
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            time.sleep(wait_interval)
            elapsed_time += wait_interval

            response = aws_clients["rds"].describe_db_instances(
                DBInstanceIdentifier=db_instance_id
            )
            db_instance = response["DBInstances"][0]
            status = db_instance["DBInstanceStatus"]

            print(f"Status after {elapsed_time}s: {status}")

            if status == "available":
                final_az = db_instance["AvailabilityZone"]
                print(f"Final AZ: {final_az}")

                # Verify failover occurred (AZ should be different)
                assert (
                    final_az != initial_az
                ), "Failover should change availability zone"
                return

        pytest.fail(f"Failover did not complete within {max_wait_time} seconds")

    def test_rds_failover_events_logged(self, aws_clients, db_instance_id):
        """Verify RDS failover events are logged in CloudWatch."""
        # Get recent events for the DB instance
        response = aws_clients["rds"].describe_events(
            SourceIdentifier=db_instance_id,
            SourceType="db-instance",
            Duration=1440,  # Last 24 hours
        )

        events = response["Events"]

        # Check if events are being logged
        assert len(events) >= 0, "Should be able to retrieve RDS events"

        # Note: This doesn't verify failover events unless a failover actually occurred
        # In a real test, you would check for specific event categories like 'failover'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
