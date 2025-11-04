# Twisted Monk Suite v1

Production-ready inventory management, lead time calculation, and Shopify integration system.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Features

### Backend API
- **FastAPI** with comprehensive error handling and validation
- **Redis caching** for optimal performance
- **Rate limiting** to prevent abuse
- **CORS & security** middleware
- **Health monitoring** endpoints
- **OpenAPI documentation** (Swagger UI)

### Shopify Integration
- **Availability badges** with real-time stock status
- **Urgency banners** to encourage purchases
- **Bundle recommendations** with smart cross-selling
- **Configurable themes** via Shopify settings
- **Responsive design** for all devices

### Operations
- **Lead time calculator** with multi-supplier support
- **Inventory monitor** with automatic alerts
- **n8n workflow** automation
- **Slack & Email notifications**
- **Multi-tier supplier management**

### Documentation
- Comprehensive setup guide
- Deployment instructions for multiple platforms
- Troubleshooting guide
- API documentation

### Testing
- Full test suite with pytest
- Backend API tests
- Inventory monitor tests
- Integration tests
- >90% code coverage

## 📁 Project Structure

```
Twisted_Monk_Suite_v1/
├── backend/              # FastAPI backend
│   ├── main.py          # Main API application
│   ├── config.py        # Configuration management
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Container image
├── shopify/             # Shopify integration
│   ├── snippets/        # Liquid snippets
│   ├── assets/          # JavaScript assets
│   └── config/          # Theme settings
├── operations/          # Operations modules
│   ├── lead_time.py     # Lead time calculator
│   ├── inventory_monitor.py  # Inventory monitor
│   └── n8n_workflow.json     # n8n automation
├── docs/                # Documentation
│   ├── SETUP.md         # Setup guide
│   ├── DEPLOYMENT.md    # Deployment guide
│   └── TROUBLESHOOTING.md   # Troubleshooting
├── tests/               # Test suite
│   ├── test_backend.py  # Backend tests
│   ├── test_inventory.py     # Inventory tests
│   └── test_integrations.py # Integration tests
├── scripts/             # Utility scripts
│   ├── deploy.sh        # Deployment script
│   ├── setup_env.sh     # Environment setup
│   └── health_check.py  # Health check tool
└── .env.example         # Environment template
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- Redis 7.0+
- Docker (optional)
- Shopify store

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd Twisted_Monk_Suite_v1

# Run setup script
./scripts/setup_env.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

### 3. Start Services

#### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

#### Manual Start

```bash
# Start Redis
redis-server

# Activate virtual environment
cd backend
source venv/bin/activate

# Run backend
uvicorn main:app --reload
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Or use the health check script
python scripts/health_check.py
```

### 5. Access Documentation

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete installation instructions
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_backend.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

## 🔌 API Endpoints

### Health & Monitoring

- `GET /health` - Health check with Redis status
- `GET /api/v1/metrics` - API metrics

### Lead Time

- `POST /api/v1/lead-time` - Calculate lead time
  ```json
  {
    "supplier_id": "SUP001",
    "product_id": "PROD-123",
    "quantity": 50
  }
  ```

### Inventory

- `GET /api/v1/inventory/{product_id}` - Get inventory status

### Bundles

- `GET /api/v1/bundles/{product_id}` - Get bundle recommendations

## 🎨 Shopify Integration

### Install Snippets

1. Go to Shopify Admin > Themes > Edit Code
2. Add snippets from `shopify/snippets/`
3. Upload assets from `shopify/assets/`
4. Configure settings in Theme Customizer

### Usage in Templates

```liquid
<!-- Availability Badge -->
{% render 'availability-badge', product: product, show_quantity: true %}

<!-- Urgency Banner -->
{% render 'urgency-banner', product: product, style: 'inline' %}

<!-- Bundle Recommendations (auto-loads via JS) -->
{{ 'bundle-recos.js' | asset_url | script_tag }}
```

## 📊 Operations

### Inventory Monitor

```python
from operations.inventory_monitor import InventoryMonitor

monitor = InventoryMonitor(check_interval_seconds=300)
# Configure and run
```

### Lead Time Calculator

```python
from operations.lead_time import LeadTimeCalculator

calculator = LeadTimeCalculator()
estimate = calculator.calculate("SUP001", "PROD-123", 50)
```

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t twisted-monk-suite:latest ./backend

# Run container
docker run -p 8000:8000 --env-file .env twisted-monk-suite:latest
```

### Cloud Platforms

The suite supports deployment to:
- AWS (ECS, Elastic Beanstalk, EC2)
- Google Cloud (Cloud Run, GKE)
- DigitalOcean App Platform
- Heroku
- Any Docker-compatible platform

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 🔧 Configuration

Key configuration options in `.env`:

```bash
# Application
DEBUG=False
PORT=8000
SECRET_KEY=your-secret-key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Shopify
SHOPIFY_API_KEY=your-api-key
SHOPIFY_SHOP_URL=yourshop.myshopify.com

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
EMAIL_SMTP_HOST=smtp.gmail.com

# Thresholds
LOW_STOCK_THRESHOLD=50
CRITICAL_STOCK_THRESHOLD=10
```

## 🔐 Security

- **Rate limiting** on all endpoints
- **Input validation** with Pydantic
- **CORS** configuration
- **Environment-based secrets**
- **TLS/SSL** support
- **Security headers** middleware
- **Non-root Docker containers**

## 📈 Monitoring

- Health check endpoint
- Prometheus metrics (optional)
- Error tracking with Sentry (optional)
- Custom logging with structured output
- n8n workflow for automated monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Email**: support@twistedmonk.com
- **Slack**: #twisted-monk-suite

## 🎯 Roadmap

- [ ] GraphQL API support
- [ ] Machine learning for demand forecasting
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Additional e-commerce platform integrations

## 📜 Changelog

### v1.0.0 (2024-11-04)

- Initial production release
- Complete backend API with FastAPI
- Shopify integration (badges, banners, bundles)
- Operations modules (lead time, inventory monitor)
- Comprehensive documentation
- Full test suite
- Deployment automation

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Shopify for the e-commerce platform
- Redis for caching
- n8n for workflow automation
- The open-source community

---

**Made with ❤️ for Twisted Monk**
