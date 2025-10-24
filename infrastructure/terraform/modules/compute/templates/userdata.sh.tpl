#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y nginx

cat <<HTML >/usr/share/nginx/html/index.html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${project_name} :: ${environment}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 3rem; background: #0f172a; color: #e2e8f0; }
    .card { max-width: 640px; margin: 0 auto; background: rgba(15, 23, 42, 0.85); padding: 2.5rem; border-radius: 18px; box-shadow: 0 20px 45px rgba(15, 23, 42, 0.55); }
    h1 { margin-top: 0; font-size: 2.4rem; }
    code { background: rgba(148, 163, 184, 0.15); padding: 0.2rem 0.4rem; border-radius: 6px; }
    .meta { margin-top: 1.5rem; font-size: 0.95rem; color: #94a3b8; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="card">
    <h1>${project_name}</h1>
    <p>This instance is part of the <strong>${project_name}</strong> deployment in the <code>${environment}</code> environment.</p>
    <div class="meta">
      <p>Region: <code>${region}</code></p>
      <p>Hostname: <code>$(hostname)</code></p>
      <p>Launched: <code>$(date -u)</code></p>
    </div>
  </div>
</body>
</html>
HTML

systemctl enable nginx
systemctl restart nginx
