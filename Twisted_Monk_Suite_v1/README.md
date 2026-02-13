# 🧘 Twisted Monk Suite v2.0

A complete, production-ready inventory management and e-commerce optimization system for Shopify stores.

## ✨ Features

### 🎯 Core Inventory Management
- **Real-time Inventory Tracking** - Live stock levels with caching
- **Automated Replenishment Alerts** - Smart lead time calculations
- **Multi-supplier Integration** - Unified supplier management

### 🚀 Customer Experience
- **Bundle Recommendations** - AI-powered product suggestions
- **Availability Badges** - Real-time stock status displays
- **Urgency Banners** - Scarcity and social proof elements

### 🔧 Operations Automation
- **Lead Time Monitoring** - Predictive inventory forecasting
- **Inventory Alerts** - Multi-channel notifications
- **n8n Workflows** - No-code automation integration

## 🏗️ Architecture

```
Frontend (Shopify Theme) ←→ Backend (FastAPI) ←→ Shopify API
       ↓                             ↓                ↓
Liquid Snippets              Redis Cache       Supplier APIs
JavaScript Components        Lead Time Calc    Email/SMS Alerts
```

## 🚀 Quick Start

1. **Backend Setup**
   ```bash
   cd Twisted_Monk_Suite_v1/backend
   cp ../.env.example .env
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Shopify Integration**
   - Upload Liquid snippets to your theme
   - Add JavaScript bundle to assets
   - Configure API endpoints

3. **Operations**
   ```bash
   cd Twisted_Monk_Suite_v1/operations
   python lead_time.py  # Generate initial report
   ```

## 📚 Documentation

- [Complete Setup Guide](docs/SETUP.md)
- [Deployment Instructions](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🛠️ Configuration

### Environment Variables
See `.env.example` for all required configuration options.

### Shopify Theme
Add these snippets to your product templates:
```liquid
{% render 'availability-badge', product: product %}
{% render 'urgency-banner', product: product %}
<div id="bundle-recos" data-bundle-recos data-product-id="{{ product.id }}"></div>
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/inventory/{id}` | GET | Product inventory levels |
| `/inventory/update` | POST | Update inventory |
| `/recommendations/bundle` | POST | Get bundle recommendations |

## 📊 Monitoring

The system includes:
- Health checks at `/health`
- Redis caching for performance
- Structured logging
- Error tracking
- Alert cooldown protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check troubleshooting guide
2. Review existing issues
3. Create a new issue with details

---

**Built with ❤️ for the Twisted Monk team**
