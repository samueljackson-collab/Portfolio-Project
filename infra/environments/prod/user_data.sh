#!/bin/bash

# ============================================================================
# File: infra/environments/prod/user_data.sh
# ============================================================================
set -euo pipefail

# Log all output
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=== Starting EC2 User Data Script ==="
echo "Environment: ${environment}"
echo "AWS Region: ${aws_region}"
echo "Date: $(date)"

# Update system packages
echo "Updating system packages..."
yum update -y

# Install essential packages
echo "Installing essential packages..."
yum install -y \
    docker \
    aws-cli \
    jq \
    htop \
    vim \
    curl \
    wget

# Install Docker Compose
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker service
echo "Starting Docker service..."
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install CloudWatch agent
echo "Installing CloudWatch agent..."
wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm
rm amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<EOF_CONFIG
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/aws/ec2/${environment}",
            "log_stream_name": "{instance_id}/messages"
          },
          {
            "file_path": "/var/log/user-data.log",
            "log_group_name": "/aws/ec2/${environment}",
            "log_stream_name": "{instance_id}/user-data"
          },
          {
            "file_path": "/var/log/docker",
            "log_group_name": "/aws/ec2/${environment}",
            "log_stream_name": "{instance_id}/docker"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "CWAgent",
    "metrics_collected": {
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DiskUsedPercent", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MemoryUsedPercent", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF_CONFIG

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Get database credentials from Secrets Manager
echo "Retrieving database credentials..."
DB_SECRET=$(aws secretsmanager get-secret-value \
    --secret-id ${secret_arn} \
    --region ${aws_region} \
    --query SecretString \
    --output text)

DB_USERNAME=$(echo $DB_SECRET | jq -r .username)
DB_PASSWORD=$(echo $DB_SECRET | jq -r .password)
DB_HOST=$(echo $DB_SECRET | jq -r .host)
DB_PORT=$(echo $DB_SECRET | jq -r .port)
DB_NAME=$(echo $DB_SECRET | jq -r .dbname)

# Create environment file for application
cat > /etc/portfolio/app.env <<EOF_ENV
DATABASE_URL=postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
ENVIRONMENT=${environment}
AWS_REGION=${aws_region}
LOG_LEVEL=INFO
EOF_ENV

chmod 600 /etc/portfolio/app.env

# Pull and run application container
if [ -n "${ecr_repo}" ]; then
    echo "Logging into ECR..."
    aws ecr get-login-password --region ${aws_region} | \
        docker login --username AWS --password-stdin ${ecr_repo}
    
    echo "Pulling application image..."
    docker pull ${ecr_repo}:latest
    
    echo "Starting application container..."
    docker run -d \
        --name portfolio-api \
        --restart unless-stopped \
        -p 8000:8000 \
        --env-file /etc/portfolio/app.env \
        --log-driver=awslogs \
        --log-opt awslogs-region=${aws_region} \
        --log-opt awslogs-group=/aws/ec2/${environment}/app \
        --log-opt awslogs-stream={instance_id} \
        ${ecr_repo}:latest
    
    echo "Application container started successfully"
else
    echo "ECR repository not configured, skipping container deployment"
    
    # Create placeholder health check
    mkdir -p /var/www/html
    cat > /var/www/html/health <<EOF_HEALTH
{"status": "healthy", "service": "portfolio-api", "environment": "${environment}"}
EOF_HEALTH
    
    # Start simple HTTP server for health checks
    python3 -m http.server 8000 --directory /var/www/html &
    echo "Placeholder health check started on port 8000"
fi

# Configure log rotation
cat > /etc/logrotate.d/portfolio <<'EOF_LOGROTATE'
/var/log/user-data.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF_LOGROTATE

# Create health check script
cat > /usr/local/bin/health-check.sh <<'SCRIPT'
#!/bin/bash
# Health check script for ALB target health
HEALTH_URL="http://localhost:8000/health"
MAX_RETRIES=3
RETRY_DELAY=2

for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "$HEALTH_URL" > /dev/null; then
        exit 0
    fi
    sleep $RETRY_DELAY
done

exit 1
SCRIPT

chmod +x /usr/local/bin/health-check.sh

# Signal success
echo "=== User Data Script Completed Successfully ==="
echo "Instance is ready to receive traffic"

# Send completion metric to CloudWatch
aws cloudwatch put-metric-data \
    --namespace "Portfolio/${environment}" \
    --metric-name "UserDataSuccess" \
    --value 1 \
    --region ${aws_region}
