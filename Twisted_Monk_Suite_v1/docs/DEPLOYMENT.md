# Twisted Monk Suite v1 - Deployment Guide

Production deployment guide for the Twisted Monk Suite.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Database Setup](#database-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Scaling](#scaling)

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All environment variables configured
- [ ] Redis instance provisioned
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Backup strategy implemented
- [ ] Monitoring tools set up
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] API rate limits configured
- [ ] Error tracking enabled (e.g., Sentry)

## Docker Deployment

### Building the Docker Image

```bash
cd backend
docker build -t twisted-monk-suite:latest .
```

### Running with Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    env_file:
      - .env
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  inventory-monitor:
    build: ./backend
    command: python -m operations.inventory_monitor
    environment:
      - REDIS_HOST=redis
    env_file:
      - .env
    depends_on:
      - redis
      - api
    restart: unless-stopped

volumes:
  redis_data:
```

Start services:

```bash
docker-compose up -d
```

### Push to Container Registry

```bash
# Docker Hub
docker tag twisted-monk-suite:latest yourusername/twisted-monk-suite:latest
docker push yourusername/twisted-monk-suite:latest

# AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag twisted-monk-suite:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/twisted-monk-suite:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/twisted-monk-suite:latest
```

## Cloud Deployment Options

### AWS (Elastic Beanstalk)

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   cd backend
   eb init -p python-3.11 twisted-monk-suite
   ```

3. **Create Environment**
   ```bash
   eb create production --instance-type t3.medium
   ```

4. **Configure Environment Variables**
   ```bash
   eb setenv DEBUG=False \
     REDIS_HOST=your-redis-endpoint \
     SECRET_KEY=your-secret-key \
     ALLOWED_HOSTS=yourdomain.com
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

### AWS (ECS Fargate)

1. **Create Task Definition**
   ```json
   {
     "family": "twisted-monk-suite",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "api",
         "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/twisted-monk-suite:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "DEBUG", "value": "False"},
           {"name": "REDIS_HOST", "value": "your-redis-endpoint"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/twisted-monk-suite",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "api"
           }
         }
       }
     ]
   }
   ```

2. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster production \
     --service-name twisted-monk-suite \
     --task-definition twisted-monk-suite \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
   ```

### Google Cloud (Cloud Run)

1. **Build and Push**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/twisted-monk-suite
   ```

2. **Deploy**
   ```bash
   gcloud run deploy twisted-monk-suite \
     --image gcr.io/PROJECT_ID/twisted-monk-suite \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DEBUG=False,REDIS_HOST=xxx
   ```

### DigitalOcean (App Platform)

1. **Create `app.yaml`**
   ```yaml
   name: twisted-monk-suite
   services:
     - name: api
       github:
         repo: your-username/twisted-monk-suite
         branch: main
         deploy_on_push: true
       source_dir: /backend
       dockerfile_path: Dockerfile
       http_port: 8000
       instance_count: 2
       instance_size_slug: professional-xs
       envs:
         - key: DEBUG
           value: "False"
         - key: REDIS_HOST
           value: ${redis.HOSTNAME}
       health_check:
         http_path: /health

   databases:
     - name: redis
       engine: REDIS
       production: true
   ```

2. **Deploy via CLI**
   ```bash
   doctl apps create --spec app.yaml
   ```

### Heroku

1. **Create Heroku App**
   ```bash
   heroku create twisted-monk-suite
   ```

2. **Add Redis**
   ```bash
   heroku addons:create heroku-redis:premium-0
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## Database Setup

### PostgreSQL (for future use)

1. **Create Database**
   ```sql
   CREATE DATABASE twisted_monk_suite;
   CREATE USER twisted_monk WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE twisted_monk_suite TO twisted_monk;
   ```

2. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

### Redis Configuration

For production, use managed Redis:

**AWS ElastiCache:**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id twisted-monk-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

**Redis Labs:**
- Sign up at https://redis.com
- Create new database
- Copy connection string

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
   ```

3. **Nginx Configuration**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name api.yourdomain.com;

       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Auto-renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

## Monitoring & Logging

### Application Monitoring

**Prometheus + Grafana:**

1. Add metrics endpoint to FastAPI:
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator
   
   Instrumentator().instrument(app).expose(app)
   ```

2. Configure Prometheus (`prometheus.yml`):
   ```yaml
   scrape_configs:
     - job_name: 'twisted-monk-suite'
       static_configs:
         - targets: ['api:8000']
   ```

### Log Aggregation

**Using Elasticsearch + Kibana:**

```python
# Configure structured logging
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

**Using CloudWatch (AWS):**

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

### Error Tracking

**Sentry Integration:**

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
    environment="production"
)
```

## Backup & Recovery

### Redis Backups

1. **Automated Backups**
   ```bash
   # Cron job for daily backups
   0 2 * * * redis-cli --rdb /backup/dump_$(date +\%Y\%m\%d).rdb
   ```

2. **Backup to S3**
   ```bash
   aws s3 cp /backup/dump.rdb s3://twisted-monk-backups/redis/
   ```

### Database Backups

```bash
# PostgreSQL backup
pg_dump twisted_monk_suite | gzip > backup_$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp backup_*.sql.gz s3://twisted-monk-backups/postgres/
```

### Recovery Procedures

1. **Redis Recovery**
   ```bash
   redis-cli SHUTDOWN
   cp /backup/dump.rdb /var/lib/redis/dump.rdb
   redis-server
   ```

2. **Database Recovery**
   ```bash
   gunzip < backup_20240101.sql.gz | psql twisted_monk_suite
   ```

## Scaling

### Horizontal Scaling

1. **Load Balancer Setup (Nginx)**
   ```nginx
   upstream twisted_monk_api {
       least_conn;
       server api1.internal:8000;
       server api2.internal:8000;
       server api3.internal:8000;
   }

   server {
       listen 80;
       location / {
           proxy_pass http://twisted_monk_api;
       }
   }
   ```

2. **Auto-scaling (AWS)**
   ```bash
   aws autoscaling create-auto-scaling-group \
     --auto-scaling-group-name twisted-monk-asg \
     --launch-configuration-name twisted-monk-lc \
     --min-size 2 \
     --max-size 10 \
     --desired-capacity 2 \
     --target-group-arns arn:aws:elasticloadbalancing:...
   ```

### Vertical Scaling

Increase instance resources:
- CPU: 2+ cores
- RAM: 4+ GB
- Redis: Increase max memory

### Caching Strategy

1. **Redis Caching Layers**
   - L1: Application cache (5 minutes)
   - L2: Redis cache (1 hour)
   - L3: Database queries

2. **CDN for Static Assets**
   - Use CloudFlare or AWS CloudFront
   - Cache Shopify assets
   - Reduce API load

## Post-Deployment

### Health Checks

Set up automated health checks:

```bash
# Health check script
#!/bin/bash
HEALTH_URL="https://api.yourdomain.com/health"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $STATUS -ne 200 ]; then
  echo "Health check failed with status $STATUS"
  # Send alert
fi
```

### Performance Testing

```bash
# Load test with Apache Bench
ab -n 10000 -c 100 https://api.yourdomain.com/health

# Or use k6
k6 run load-test.js
```

### Security Hardening

- Enable firewall rules
- Implement rate limiting
- Use secrets management (AWS Secrets Manager, Vault)
- Regular security audits
- Keep dependencies updated

## Rollback Procedures

If deployment fails:

1. **Docker Compose**
   ```bash
   docker-compose down
   git checkout previous-version
   docker-compose up -d
   ```

2. **Cloud Platforms**
   ```bash
   # AWS ECS
   aws ecs update-service --service twisted-monk-suite --task-definition previous-revision
   
   # Heroku
   heroku releases:rollback
   ```

## Support

For deployment assistance:
- Email: devops@twistedmonk.com
- Slack: #deployment-support
- Documentation: https://docs.twistedmonk.com
