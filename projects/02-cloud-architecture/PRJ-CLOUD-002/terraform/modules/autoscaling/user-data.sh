#!/bin/bash
set -euo pipefail

yum update -y
amazon-linux-extras enable nginx1
yum install -y nginx

cat <<'HTML' >/usr/share/nginx/html/index.html
<html>
  <head>
    <title>AWS Multi-Tier Reference</title>
  </head>
  <body>
    <h1>Application Tier Ready</h1>
    <p>This instance was provisioned by Terraform as part of the multi-tier AWS reference architecture.</p>
  </body>
</html>
HTML

systemctl enable nginx
systemctl restart nginx
