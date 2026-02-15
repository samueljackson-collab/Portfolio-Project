# Twisted Monk Suite v1 - Setup Guide

Complete setup guide for deploying the Twisted Monk Suite inventory management system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Shopify Integration](#shopify-integration)
- [Operations Setup](#operations-setup)
- [Configuration](#configuration)
- [Testing](#testing)

## Prerequisites

### Required Software

- Python 3.11 or higher
- Redis 7.0 or higher
- Node.js 18+ (for Shopify theme development)
- Docker and Docker Compose (optional, for containerized deployment)
- n8n (for workflow automation)

### Required Accounts

- Shopify store with admin access
- Slack workspace (for alerts)
- Email SMTP server access
- Cloud hosting account (AWS, GCP, DigitalOcean, etc.)

### API Keys & Credentials

You'll need the following credentials:

- Shopify API key and secret
- Shopify shop URL
- Slack webhook URL
- Email SMTP credentials
- Redis connection details

## Backend Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Twisted_Monk_Suite_v1/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp ../.env.example .env
```

Edit `.env` with your configuration:

```env
# Application
DEBUG=False
PORT=8000
SECRET_KEY=your-secret-key-here

# Security
ALLOWED_HOSTS=yourdomain.com,*.yourdomain.com
ALLOWED_ORIGINS=https://yourshop.myshopify.com,https://yourdomain.com

# Redis
REDIS_ENABLED=True
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
CACHE_TTL=3600

# Shopify
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
SHOPIFY_SHOP_URL=yourshop.myshopify.com

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=alerts@twistedmonk.com
EMAIL_TO=team@twistedmonk.com,inventory@twistedmonk.com

# Thresholds
LOW_STOCK_THRESHOLD=50
CRITICAL_STOCK_THRESHOLD=10
```

### 5. Start Redis (if not using cloud service)

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or install locally
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu
```

### 6. Run the Backend

#### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode (with Gunicorn)

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 7. Verify Installation

Open your browser to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Expected health check response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "redis_connected": true,
  "timestamp": 1234567890.123
}
```

## Shopify Integration

### 1. Install Theme Files

#### Upload Snippets

1. Go to your Shopify admin: `Online Store > Themes > Actions > Edit code`
2. Navigate to `Snippets` folder
3. Create new snippets:
   - `availability-badge.liquid` - Copy content from `shopify/snippets/availability-badge.liquid`
   - `urgency-banner.liquid` - Copy content from `shopify/snippets/urgency-banner.liquid`

#### Upload Assets

1. Navigate to `Assets` folder
2. Upload `shopify/assets/bundle-recos.js`

#### Configure Settings

1. Navigate to `Config` folder
2. Update `settings_schema.json` by merging content from `shopify/config/settings_schema.json`

### 2. Add Snippets to Product Template

Edit your product template (`sections/product-template.liquid` or similar):

```liquid
<!-- Add availability badge -->
<div class="product__availability">
  {% render 'availability-badge', product: product, show_quantity: true %}
</div>

<!-- Add urgency banner -->
<div class="product__urgency">
  {% render 'urgency-banner', product: product, style: 'inline' %}
</div>

<!-- Bundle recommendations will auto-load via JavaScript -->
```

### 3. Include Bundle Recommendations Script

Add to your theme's `layout/theme.liquid` before `</body>`:

```liquid
{{ 'bundle-recos.js' | asset_url | script_tag }}
```

### 4. Configure Theme Settings

1. Go to `Online Store > Themes > Customize`
2. Navigate to Theme Settings
3. Find "Twisted Monk Suite" sections
4. Configure:
   - Stock thresholds
   - Badge colors
   - API endpoints
   - Notification preferences

## Operations Setup

### 1. Lead Time Calculator

The lead time calculator runs as part of the backend API. To use it standalone:

```python
from operations.lead_time import LeadTimeCalculator

calculator = LeadTimeCalculator()

# Calculate lead time
estimate = calculator.calculate(
    supplier_id="SUP001",
    product_id="PROD-123",
    quantity=50
)

print(f"Estimated lead time: {estimate.estimated_days} days")
```

### 2. Inventory Monitor

Set up the inventory monitor to run continuously:

```python
import asyncio
from operations.inventory_monitor import InventoryMonitor, SlackNotifier, EmailNotifier

# Create monitor
monitor = InventoryMonitor(check_interval_seconds=300)

# Add notifiers
slack = SlackNotifier(webhook_url="YOUR_SLACK_WEBHOOK")
monitor.add_notifier(slack)

email = EmailNotifier(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-password",
    from_addr="alerts@twistedmonk.com",
    to_addrs=["team@twistedmonk.com"]
)
monitor.add_notifier(email)

# Run monitor
asyncio.run(monitor.run())
```

#### Running as a Service (systemd)

Create `/etc/systemd/system/twisted-monk-monitor.service`:

```ini
[Unit]
Description=Twisted Monk Inventory Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/twisted-monk-suite/operations
Environment="PATH=/opt/twisted-monk-suite/venv/bin"
ExecStart=/opt/twisted-monk-suite/venv/bin/python -m inventory_monitor
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable twisted-monk-monitor
sudo systemctl start twisted-monk-monitor
```

### 3. n8n Workflow Setup

#### Install n8n

```bash
npm install -g n8n
```

#### Import Workflow

1. Start n8n: `n8n start`
2. Open: http://localhost:5678
3. Click "Workflows" > "Import from File"
4. Select `operations/n8n_workflow.json`
5. Configure environment variables in n8n:
   - `API_BASE_URL`: Your backend API URL
   - `SLACK_WEBHOOK_URL`: Slack webhook
   - `EMAIL_FROM`, `EMAIL_TO`: Email settings
   - `ADMIN_URL`: Your admin dashboard URL
   - `AIRTABLE_BASE_ID`: (optional) Airtable base ID

#### Activate Workflow

1. Review all nodes and connections
2. Test each node individually
3. Click "Active" to enable the workflow

## Configuration

### Backend Configuration

All backend configuration is in `backend/config.py`. Key settings:

```python
# Modify in .env file
DEBUG=False  # Set to True only in development
PORT=8000
CACHE_TTL=3600  # Cache timeout in seconds
LOW_STOCK_THRESHOLD=50
CRITICAL_STOCK_THRESHOLD=10
```

### Shopify Configuration

Configure via Theme Settings in Shopify admin:
- Stock thresholds
- Badge colors and positions
- Bundle recommendations
- API endpoints
- Cache settings

### Redis Configuration

For production, use a managed Redis service:
- AWS ElastiCache
- Redis Labs
- DigitalOcean Managed Databases

Connection string format:
```
redis://:[password]@[host]:[port]/[db]
```

## Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v --cov
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Lead time calculation
curl -X POST http://localhost:8000/api/v1/lead-time \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "SUP001",
    "product_id": "PROD-123",
    "quantity": 50
  }'

# Inventory status
curl http://localhost:8000/api/v1/inventory/PROD-123
```

### Test Shopify Integration

1. Visit a product page on your Shopify store
2. Verify availability badge appears
3. Check urgency banner displays for low-stock items
4. Scroll down to see bundle recommendations
5. Check browser console for any JavaScript errors

### Test Notifications

```bash
# Test Slack notification
python operations/inventory_monitor.py --test-slack

# Test email notification
python operations/inventory_monitor.py --test-email
```

## Next Steps

After setup is complete:

1. Review the [DEPLOYMENT.md](DEPLOYMENT.md) guide for production deployment
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues
3. Set up monitoring and logging
4. Configure backup procedures
5. Set up SSL certificates for production

## Support

For issues or questions:
- Check the troubleshooting guide
- Review API documentation at `/docs`
- Contact support: support@twistedmonk.com
