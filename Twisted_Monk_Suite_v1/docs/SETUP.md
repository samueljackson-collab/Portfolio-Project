# Twisted Monk Suite - Complete Setup Guide

## Prerequisites

- Python 3.9+
- Redis 6+
- Shopify Store
- Server/VM for hosting

## 1. Backend Setup

### Environment Configuration
```bash
cp .env.example .env
# Edit .env with your actual values
```

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Running the Server
```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
docker build -t twisted-monk-api .
docker run -d -p 8000:8000 --env-file .env twisted-monk-api
```

## 2. Shopify Integration

### Adding Liquid Snippets
1. Go to Shopify Admin → Themes → Edit Code
2. Add files from `shopify/snippets/` to your theme snippets
3. Add `shopify/assets/bundle-recos.js` to your theme assets
4. Update `config/settings_schema.json` if needed

### Using the Snippets
```liquid
{% comment %} Product template {% endcomment %}
{% render 'availability-badge', product: product %}
{% render 'urgency-banner', product: product %}

{% comment %} Bundle recommendations {% endcomment %}
<div id="bundle-recos" 
     data-bundle-recos
     data-api-base-url="https://your-api.com"
     data-product-id="{{ product.id }}"
     data-limit="4">
</div>
```

## 3. Operations Setup

### Lead Time Calculator
```bash
cd operations
python lead_time.py
```

### Inventory Monitor
```bash
# One-time check
python inventory_monitor.py

# Continuous monitoring
python -c "from inventory_monitor import InventoryMonitor; import asyncio; asyncio.run(InventoryMonitor().run_continuous_monitoring())"
```

## 4. n8n Workflow Setup

1. Import `operations/n8n_workflow.json` into n8n
2. Configure Shopify and email nodes
3. Set up triggers and schedules

## 5. Testing

```bash
# Run all tests
pytest tests/

# Test specific components
pytest tests/test_backend.py
pytest tests/test_inventory.py
```

## 6. Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Redis server running
- [ ] API endpoints accessible from Shopify
- [ ] Error monitoring configured
- [ ] Backup strategy in place
