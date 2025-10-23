#!/bin/bash
set -euo pipefail

echo "Configuring ${environment} environment" > /var/log/bootstrap.log
yum update -y
amazon-linux-extras enable nginx1
yum install -y nginx jq

cat <<'NGINX_CONF' > /etc/nginx/conf.d/app.conf
server {
    listen ${app_port};
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /healthz {
        return 200 'ok';
        add_header Content-Type text/plain;
    }
}
NGINX_CONF

systemctl enable nginx
systemctl restart nginx

echo "LOG_LEVEL=${log_level}" > /etc/app.env

