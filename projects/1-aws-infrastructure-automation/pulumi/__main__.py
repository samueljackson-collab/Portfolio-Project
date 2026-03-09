"""Pulumi program that provisions the AWS footprint defined for Project 1."""

import pulumi
import pulumi_aws as aws

STACK = pulumi.get_stack()
CONFIG = pulumi.Config()
ENVIRONMENT = CONFIG.get("environment") or "dev"
REGION = CONFIG.get("region") or "us-west-2"
DB_USERNAME = CONFIG.require("dbUsername")
DB_PASSWORD = CONFIG.require_secret("dbPassword")

aws.config.region = REGION

vpc = aws.ec2.Vpc(
    f"portfolio-vpc-{ENVIRONMENT}",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Project": "portfolio",
        "Environment": ENVIRONMENT,
        "AutoRecover": "true",
    },
)

availability_zones = aws.get_availability_zones()

public_subnets = []
private_subnets = []
database_subnets = []

for index, az in enumerate(availability_zones.names[:3]):
    public = aws.ec2.Subnet(
        f"public-{az}-{ENVIRONMENT}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{index + 1}.0/24",
        availability_zone=az,
        map_public_ip_on_launch=True,
        tags={"Tier": "public"},
    )
    public_subnets.append(public)

    private = aws.ec2.Subnet(
        f"private-{az}-{ENVIRONMENT}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{index + 11}.0/24",
        availability_zone=az,
        tags={"Tier": "private"},
    )
    private_subnets.append(private)

    database = aws.ec2.Subnet(
        f"database-{az}-{ENVIRONMENT}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{index + 21}.0/24",
        availability_zone=az,
        tags={"Tier": "database"},
    )
    database_subnets.append(database)

rds_subnet_group = aws.rds.SubnetGroup(
    f"portfolio-db-subnets-{ENVIRONMENT}",
    subnet_ids=[subnet.id for subnet in database_subnets],
)

security_group = aws.ec2.SecurityGroup(
    f"portfolio-core-sg-{ENVIRONMENT}",
    description="Core security group for the portfolio infrastructure",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp", from_port=5432, to_port=5432, cidr_blocks=["10.0.0.0/16"]
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
        )
    ],
)

cluster = aws.eks.Cluster(
    f"portfolio-eks-{ENVIRONMENT}",
    role_arn=CONFIG.require("eksRoleArn"),
    vpc_config=aws.eks.ClusterVpcConfigArgs(
        subnet_ids=[subnet.id for subnet in private_subnets],
        security_group_ids=[security_group.id],
    ),
)

node_group = aws.eks.NodeGroup(
    f"portfolio-nodes-{ENVIRONMENT}",
    cluster_name=cluster.name,
    node_role_arn=CONFIG.require("nodeRoleArn"),
    subnet_ids=[subnet.id for subnet in private_subnets],
    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        desired_size=3,
        max_size=10,
        min_size=2,
    ),
    capacity_type="SPOT",
    instance_types=["t3.medium", "t3.large", "t2.medium"],
)

rds_instance = aws.rds.Instance(
    f"portfolio-db-{ENVIRONMENT}",
    allocated_storage=20,
    max_allocated_storage=100,
    engine="postgres",
    engine_version="15.4",
    instance_class="db.t3.medium",
    name="portfolio",
    username=DB_USERNAME,
    password=DB_PASSWORD,
    db_subnet_group_name=rds_subnet_group.name,
    vpc_security_group_ids=[security_group.id],
    backup_retention_period=7,
    skip_final_snapshot=ENVIRONMENT != "production",
)

pulumi.export("vpcId", vpc.id)
pulumi.export("eksClusterName", cluster.name)
pulumi.export("rdsEndpoint", rds_instance.address)
