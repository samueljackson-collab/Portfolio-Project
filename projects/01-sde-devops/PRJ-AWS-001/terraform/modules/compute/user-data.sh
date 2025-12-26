#!/bin/bash
set -euo pipefail

LOG_GROUP_NAME="${log_group_name}"
APP_LOG_PATH="${app_log_path}"
CW_AGENT_CONFIG_PATH="/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json"

mkdir -p "$(dirname "$APP_LOG_PATH")"
touch "$APP_LOG_PATH"

install_packages() {
  if command -v yum >/dev/null 2>&1; then
    yum update -y
    yum install -y amazon-cloudwatch-agent docker
    systemctl enable --now docker
    return 0
  fi

  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -y
    apt-get install -y docker.io wget
    systemctl enable --now docker

    # Download and install CloudWatch agent for Debian/Ubuntu
    wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb -O /tmp/amazon-cloudwatch-agent.deb
    dpkg -i -E /tmp/amazon-cloudwatch-agent.deb
    rm /tmp/amazon-cloudwatch-agent.deb
    return 0
  fi

  return 1
}

if ! install_packages; then
  echo "Failed to install amazon-cloudwatch-agent via package manager" >&2
  exit 1
fi

cat > "$CW_AGENT_CONFIG_PATH" <<EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "${app_log_path}",
            "log_group_name": "${log_group_name}",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c "file:${CW_AGENT_CONFIG_PATH}" \
  -s
