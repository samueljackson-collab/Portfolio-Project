//go:build integration
// +build integration

package integration

import (
	"fmt"
	"net"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/applicationautoscaling"
	"github.com/aws/aws-sdk-go/service/elbv2"
	"github.com/aws/aws-sdk-go/service/rds"
	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/retry"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

type vpcDeployment struct {
	vpcID           string
	publicSubnets   []string
	privateSubnets  []string
	databaseSubnets []string
}

func requireIntegrationEnv(t *testing.T) (string, string) {
	t.Helper()

	if os.Getenv("RUN_TERRATEST") == "" {
		t.Skip("Set RUN_TERRATEST=true to enable live Terraform integration tests")
	}

	region := os.Getenv("AWS_REGION")
	if region == "" {
		region = os.Getenv("AWS_DEFAULT_REGION")
	}

	if region == "" {
		t.Skip("AWS_REGION or AWS_DEFAULT_REGION must be set")
	}

	return region, fmt.Sprintf("pp-int-%s", strings.ToLower(random.UniqueId()))
}

func deployVpc(t *testing.T, region, name string) vpcDeployment {
	t.Helper()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: filepath.Join("..", "..", "infrastructure", "terraform", "modules", "vpc"),
		Vars: map[string]interface{}{
			"project_name":             name,
			"environment":              "int",
			"enable_nat_gateway":       false,
			"single_nat_gateway":       true,
			"enable_flow_logs":         false,
			"enable_s3_endpoint":       false,
			"flow_logs_retention_days": 1,
			"tags":                     map[string]string{"Owner": "terratest"},
		},
		EnvVars: map[string]string{
			"AWS_DEFAULT_REGION": region,
		},
		NoColor: true,
	})

	terraform.InitAndApply(t, terraformOptions)

	deployment := vpcDeployment{
		vpcID:           terraform.Output(t, terraformOptions, "vpc_id"),
		publicSubnets:   terraform.OutputList(t, terraformOptions, "public_subnet_ids"),
		privateSubnets:  terraform.OutputList(t, terraformOptions, "private_subnet_ids"),
		databaseSubnets: terraform.OutputList(t, terraformOptions, "database_subnet_ids"),
	}

	t.Cleanup(func() {
		terraform.Destroy(t, terraformOptions)
	})

	require.NotEmpty(t, deployment.vpcID)
	require.NotEmpty(t, deployment.publicSubnets)
	require.NotEmpty(t, deployment.privateSubnets)

	return deployment
}

func TestNetworkingModuleProvisioning(t *testing.T) {
	region, projectName := requireIntegrationEnv(t)

	vpc := deployVpc(t, region, projectName)
	require.GreaterOrEqual(t, len(vpc.publicSubnets), 1)
	require.GreaterOrEqual(t, len(vpc.privateSubnets), 1)
}

func TestEcsModuleAlbAndAutoscaling(t *testing.T) {
	region, projectName := requireIntegrationEnv(t)

	vpc := deployVpc(t, region, projectName+"-ecs")

	ecsTerraform := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: filepath.Join("..", "..", "infrastructure", "terraform", "modules", "ecs-application"),
		Vars: map[string]interface{}{
			"project_name":        projectName,
			"environment":         "int",
			"vpc_id":              vpc.vpcID,
			"public_subnet_ids":   vpc.publicSubnets,
			"private_subnet_ids":  vpc.privateSubnets,
			"container_image":     "public.ecr.aws/docker/library/nginx:latest",
			"container_port":      80,
			"health_check_path":   "/",
			"enable_autoscaling":  true,
			"min_capacity":        1,
			"max_capacity":        2,
			"desired_count":       1,
			"cpu_target_value":    50.0,
			"memory_target_value": 50.0,
			"tags": map[string]string{
				"Owner": "terratest",
			},
		},
		EnvVars: map[string]string{
			"AWS_DEFAULT_REGION": region,
		},
		NoColor: true,
	})

	terraform.InitAndApply(t, ecsTerraform)
	t.Cleanup(func() {
		terraform.Destroy(t, ecsTerraform)
	})

	tgArn := terraform.Output(t, ecsTerraform, "target_group_arn")
	albDNS := terraform.Output(t, ecsTerraform, "alb_dns_name")
	autoscalingTarget := terraform.Output(t, ecsTerraform, "autoscaling_target_id")

	require.NotEmpty(t, tgArn)
	require.NotEmpty(t, albDNS)
	require.NotEmpty(t, autoscalingTarget)

	sess := awsSession(t, region)
	assertTargetGroupHealthCheck(t, sess, tgArn, "/")
	assertAutoscalingWindow(t, sess, autoscalingTarget, 1, 2)

	retry.DoWithRetry(t, "wait-for-alb", 10, 30*time.Second, func() (string, error) {
		conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:80", albDNS), 10*time.Second)
		if err != nil {
			return "alb not reachable yet", err
		}
		defer conn.Close()
		return "alb reachable", nil
	})
}

func TestDatabaseModuleConnectivity(t *testing.T) {
	region, projectName := requireIntegrationEnv(t)
	vpc := deployVpc(t, region, projectName+"-db")

	dbTerraform := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: filepath.Join("..", "..", "infrastructure", "terraform", "modules", "database"),
		Vars: map[string]interface{}{
			"project_name":               projectName,
			"environment":                "int",
			"vpc_id":                     vpc.vpcID,
			"subnet_ids":                 vpc.databaseSubnets,
			"db_username":                "terratest",
			"db_password":                "SuperSecretPass123!",
			"multi_az":                   false,
			"backup_retention_period":    1,
			"skip_final_snapshot":        true,
			"apply_immediately":          true,
			"allowed_security_group_ids": []string{},
			"tags":                       map[string]string{"Owner": "terratest"},
		},
		EnvVars: map[string]string{
			"AWS_DEFAULT_REGION": region,
		},
		NoColor: true,
	})

	terraform.InitAndApply(t, dbTerraform)
	t.Cleanup(func() {
		terraform.Destroy(t, dbTerraform)
	})

	endpoint := terraform.Output(t, dbTerraform, "db_endpoint")
	dbSecurityGroup := terraform.Output(t, dbTerraform, "db_security_group_id")

	require.NotEmpty(t, endpoint)
	require.NotEmpty(t, dbSecurityGroup)

	sess := awsSession(t, region)
	assertRdsAvailable(t, sess, endpoint)
}

func awsSession(t *testing.T, region string) *session.Session {
	t.Helper()

	sess, err := session.NewSession(&aws.Config{Region: aws.String(region)})
	require.NoError(t, err)
	return sess
}

func assertTargetGroupHealthCheck(t *testing.T, sess *session.Session, targetGroupArn, expectedPath string) {
	t.Helper()

	client := elbv2.New(sess)
	out, err := client.DescribeTargetGroups(&elbv2.DescribeTargetGroupsInput{TargetGroupArns: aws.StringSlice([]string{targetGroupArn})})
	require.NoError(t, err)
	require.Len(t, out.TargetGroups, 1)

	actual := aws.StringValue(out.TargetGroups[0].HealthCheckPath)
	require.Equal(t, expectedPath, actual)
}

func assertAutoscalingWindow(t *testing.T, sess *session.Session, targetID string, min, max int64) {
	t.Helper()

	client := applicationautoscaling.New(sess)
	out, err := client.DescribeScalableTargets(&applicationautoscaling.DescribeScalableTargetsInput{
		ResourceIds:       aws.StringSlice([]string{targetID}),
		ScalableDimension: aws.String("ecs:service:DesiredCount"),
		ServiceNamespace:  aws.String("ecs"),
	})
	require.NoError(t, err)
	require.Len(t, out.ScalableTargets, 1)

	require.Equal(t, min, aws.Int64Value(out.ScalableTargets[0].MinCapacity))
	require.Equal(t, max, aws.Int64Value(out.ScalableTargets[0].MaxCapacity))
}

func assertRdsAvailable(t *testing.T, sess *session.Session, endpoint string) {
	t.Helper()

	host := endpoint
	if strings.Contains(endpoint, ":") {
		parsed, err := url.Parse(fmt.Sprintf("postgres://%s", endpoint))
		require.NoError(t, err)
		host = parsed.Hostname()
	}

	client := rds.New(sess)
	retry.DoWithRetry(t, "rds-available", 30, 60*time.Second, func() (string, error) {
		out, err := client.DescribeDBInstances(&rds.DescribeDBInstancesInput{})
		if err != nil {
			return "describe", err
		}

		for _, inst := range out.DBInstances {
			if strings.Contains(aws.StringValue(inst.Endpoint.Address), host) {
				if aws.StringValue(inst.DBInstanceStatus) == "available" {
					return "available", nil
				}
				return "waiting", fmt.Errorf("db instance status: %s", aws.StringValue(inst.DBInstanceStatus))
			}
		}
		return "not-found", fmt.Errorf("endpoint %s not present in describe output", host)
	})
}
