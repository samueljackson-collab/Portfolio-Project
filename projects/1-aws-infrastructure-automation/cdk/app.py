#!/usr/bin/env python3
"""AWS CDK application that mirrors the Terraform footprint for the portfolio."""
from aws_cdk import (
    App,
    Duration,
    Environment,
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_rds as rds,
)
from constructs import Construct


class PortfolioStack(Stack):
    """Defines the network, EKS, and database resources for the project."""

    def __init__(
        self, scope: Construct, construct_id: str, *, environment_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "PortfolioVpc",
            max_azs=3,
            nat_gateways=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        cluster = eks.Cluster(
            self,
            "PortfolioEks",
            version=eks.KubernetesVersion.V1_28,
            vpc=vpc,
            default_capacity=2,
            default_capacity_instance=ec2.InstanceType("t3.medium"),
        )

        cluster.add_nodegroup_capacity(
            "SpotNodes",
            instance_types=[
                ec2.InstanceType("t3.medium"),
                ec2.InstanceType("t3.large"),
            ],
            min_size=1,
            max_size=10,
            capacity_type=eks.CapacityType.SPOT,
        )

        rds.DatabaseInstance(
            self,
            "PortfolioDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM
            ),
            allocated_storage=20,
            max_allocated_storage=100,
            multi_az=True,
            deletion_protection=environment_name == "production",
            removal_policy=(
                RemovalPolicy.SNAPSHOT
                if environment_name == "production"
                else RemovalPolicy.DESTROY
            ),
            backup_retention=Duration.days(7),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
        )


app = App()
PortfolioStack(
    app,
    "PortfolioStack",
    environment_name=app.node.try_get_context("environment") or "dev",
    env=Environment(region="us-west-2"),
)
app.synth()
