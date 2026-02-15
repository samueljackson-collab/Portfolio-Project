# Twisted Monk Suite v1 - Troubleshooting Guide

Common issues and their solutions for the Twisted Monk Suite.

## Table of Contents

- [Backend Issues](#backend-issues)
- [Redis Connection Issues](#redis-connection-issues)
- [Shopify Integration Issues](#shopify-integration-issues)
- [API Errors](#api-errors)
- [Performance Issues](#performance-issues)
- [Notification Issues](#notification-issues)
- [Deployment Issues](#deployment-issues)

## Backend Issues

### Application Won't Start

**Symptom:** FastAPI application fails to start

**Common Causes:**

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

2. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Invalid environment variables**
   ```bash
   # Check .env file exists and is properly formatted
   cat .env
   # Validate required variables
   python -c "from config import settings; print(settings)"
   ```

**Solution:**
```bash
# Clean restart
pkill -f uvicorn
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Import Errors

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```bash
# Ensure you're in the correct directory
cd backend

# Verify Python path
echo $PYTHONPATH

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run as module
python -m main
```

### Configuration Issues

**Symptom:** Settings not loading correctly

**Debugging:**
```python
# Test config loading
python -c "
from config import settings
import json
print(json.dumps({
    'DEBUG': settings.DEBUG,
    'REDIS_URL': settings.REDIS_URL,
    'PORT': settings.PORT
}, indent=2))
"
```

## Redis Connection Issues

### Cannot Connect to Redis

**Symptom:** `redis.exceptions.ConnectionError`

**Checklist:**
1. ✓ Redis server is running
2. ✓ Correct host and port
3. ✓ Network connectivity
4. ✓ Authentication credentials

**Solutions:**

1. **Check Redis is running**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Start Redis if not running**
   ```bash
   # Docker
   docker start redis
   
   # Local
   redis-server
   
   # Service
   sudo systemctl start redis
   ```

3. **Test connection**
   ```bash
   redis-cli -h localhost -p 6379 -a yourpassword ping
   ```

4. **Check firewall rules**
   ```bash
   # Allow Redis port
   sudo ufw allow 6379/tcp
   ```

### Redis Authentication Failed

**Symptom:** `NOAUTH Authentication required`

**Solution:**
```bash
# Update .env file
REDIS_PASSWORD=your-redis-password

# Test with password
redis-cli -a your-redis-password ping
```

### Redis Out of Memory

**Symptom:** `OOM command not allowed when used memory > 'maxmemory'`

**Solutions:**

1. **Increase max memory**
   ```bash
   # Edit redis.conf
   maxmemory 2gb
   maxmemory-policy allkeys-lru
   ```

2. **Clear cache**
   ```bash
   redis-cli FLUSHDB
   ```

3. **Monitor memory usage**
   ```bash
   redis-cli INFO memory
   ```

## Shopify Integration Issues

### Snippets Not Displaying

**Symptom:** Availability badge or urgency banner not showing

**Debugging:**

1. **Check snippet installation**
   - Go to Shopify Admin > Themes > Edit Code
   - Verify snippets exist in Snippets folder

2. **Check theme integration**
   ```liquid
   {% comment %} Add to product template {% endcomment %}
   {% render 'availability-badge', product: product %}
   ```

3. **Check browser console**
   - Open DevTools (F12)
   - Look for JavaScript errors
   - Check Network tab for failed requests

4. **Verify product data**
   ```liquid
   {{ product.selected_or_first_available_variant.inventory_quantity }}
   ```

**Common Issues:**

1. **Variant not available**
   ```liquid
   {% if product.selected_or_first_available_variant %}
     {% render 'availability-badge', product: product %}
   {% else %}
     <p>No variants available</p>
   {% endif %}
   ```

2. **Inventory tracking not enabled**
   - Enable in Shopify: Product > Variants > Track quantity

### Bundle Recommendations Not Loading

**Symptom:** Bundle recommendations section doesn't appear

**Debugging:**

1. **Check JavaScript is loaded**
   ```javascript
   // In browser console
   console.log(typeof window.BundleRecommendations);
   // Should output: "function"
   ```

2. **Check API endpoint**
   ```bash
   curl https://yoursite.com/apps/twisted-monk/api/bundles/product-id
   ```

3. **Check browser console**
   ```javascript
   // Look for errors related to bundle-recos.js
   ```

**Solutions:**

1. **Verify script inclusion**
   ```liquid
   {{ 'bundle-recos.js' | asset_url | script_tag }}
   ```

2. **Check API configuration**
   ```javascript
   // In Theme Settings
   api_base_url: "https://api.yourdomain.com"
   ```

3. **Manual initialization**
   ```javascript
   // In browser console
   const bundles = new BundleRecommendations({
     apiEndpoint: '/your-endpoint',
     enableAutoDisplay: true
   });
   ```

## API Errors

### 422 Unprocessable Entity

**Symptom:** Validation errors when calling API

**Example Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**Solution:**
Ensure request body matches expected schema:
```bash
curl -X POST http://localhost:8000/api/v1/lead-time \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "SUP001",
    "product_id": "PROD-123",
    "quantity": 50
  }'
```

### 429 Too Many Requests

**Symptom:** Rate limit exceeded

**Solution:**
```python
# Increase rate limits in main.py
@limiter.limit("100/minute")  # Instead of 30/minute
async def calculate_lead_time(request: Request, ...):
    ...
```

Or implement exponential backoff:
```python
import time

def api_call_with_retry(url, max_retries=3):
    for i in range(max_retries):
        response = requests.get(url)
        if response.status_code != 429:
            return response
        time.sleep(2 ** i)  # Exponential backoff
    raise Exception("Rate limit exceeded")
```

### 500 Internal Server Error

**Symptom:** Unexpected server error

**Debugging:**

1. **Check application logs**
   ```bash
   # Docker
   docker-compose logs api
   
   # Systemd
   sudo journalctl -u twisted-monk-api -f
   
   # Local
   tail -f app.log
   ```

2. **Enable debug mode temporarily**
   ```python
   # In .env
   DEBUG=True
   ```

3. **Check error details**
   ```bash
   curl -v http://localhost:8000/api/endpoint
   ```

## Performance Issues

### Slow API Response Times

**Symptoms:**
- Requests taking > 2 seconds
- Timeouts
- Poor user experience

**Diagnostics:**

1. **Check API metrics**
   ```bash
   curl http://localhost:8000/api/v1/metrics
   ```

2. **Monitor response times**
   ```bash
   # Check X-Process-Time header
   curl -I http://localhost:8000/api/v1/inventory/PROD-123
   ```

3. **Redis performance**
   ```bash
   redis-cli --latency
   redis-cli --latency-history
   ```

**Solutions:**

1. **Increase cache TTL**
   ```python
   # In config.py
   CACHE_TTL = 7200  # 2 hours instead of 1
   ```

2. **Add database indexes**
   ```sql
   CREATE INDEX idx_product_id ON inventory(product_id);
   ```

3. **Optimize queries**
   ```python
   # Use select_related / prefetch_related
   products = Product.objects.select_related('supplier').all()
   ```

4. **Scale horizontally**
   - Add more API instances
   - Use load balancer
   - Implement CDN

### High Memory Usage

**Symptom:** Server running out of memory

**Diagnostics:**
```bash
# Check memory usage
free -h
docker stats

# Check Python process
ps aux | grep python
```

**Solutions:**

1. **Limit worker processes**
   ```bash
   # Reduce workers
   gunicorn main:app -w 2  # Instead of 4
   ```

2. **Implement pagination**
   ```python
   @app.get("/api/v1/products")
   async def list_products(page: int = 1, page_size: int = 50):
       ...
   ```

3. **Clear cache periodically**
   ```bash
   redis-cli FLUSHDB
   ```

## Notification Issues

### Slack Notifications Not Sending

**Symptom:** No messages appearing in Slack

**Debugging:**

1. **Test webhook URL**
   ```bash
   curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
     -H 'Content-Type: application/json' \
     -d '{"text": "Test message"}'
   ```

2. **Check webhook URL**
   ```python
   # Verify in .env
   echo $SLACK_WEBHOOK_URL
   ```

3. **Check logs**
   ```bash
   grep -i "slack" app.log
   ```

**Solutions:**

1. **Regenerate webhook**
   - Go to Slack App settings
   - Create new incoming webhook
   - Update `.env` file

2. **Check Slack app permissions**
   - Ensure app has `chat:write` scope

### Email Notifications Not Sending

**Symptom:** No emails received

**Debugging:**

1. **Test SMTP connection**
   ```python
   import smtplib
   
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-password')
   server.quit()
   print("SMTP connection successful")
   ```

2. **Check email logs**
   ```bash
   grep -i "email" app.log
   ```

**Solutions:**

1. **Use app-specific password (Gmail)**
   - Enable 2FA
   - Generate app password
   - Use app password in `.env`

2. **Check spam folder**

3. **Verify SMTP settings**
   ```python
   # In .env
   EMAIL_SMTP_HOST=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

## Deployment Issues

### Docker Build Fails

**Symptom:** `docker build` command fails

**Common Issues:**

1. **Requirements installation fails**
   ```dockerfile
   # Add --no-cache-dir
   RUN pip install --no-cache-dir -r requirements.txt
   ```

2. **Permission denied**
   ```bash
   sudo docker build -t twisted-monk-suite .
   ```

3. **Out of disk space**
   ```bash
   docker system prune -a
   ```

### Container Won't Start

**Symptom:** Docker container exits immediately

**Debugging:**
```bash
# Check logs
docker logs twisted-monk-suite

# Check exit code
docker inspect twisted-monk-suite | grep ExitCode
```

**Solutions:**

1. **Check environment variables**
   ```bash
   docker run --env-file .env twisted-monk-suite
   ```

2. **Test locally first**
   ```bash
   docker run -it twisted-monk-suite /bin/bash
   # Then run commands manually
   ```

### SSL Certificate Issues

**Symptom:** HTTPS not working, certificate errors

**Solutions:**

1. **Renew Let's Encrypt certificate**
   ```bash
   sudo certbot renew
   sudo systemctl reload nginx
   ```

2. **Check certificate expiry**
   ```bash
   echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
   ```

## Getting Help

If you can't resolve your issue:

1. **Check logs first**
   ```bash
   # Application logs
   tail -f app.log
   
   # System logs
   journalctl -xe
   ```

2. **Collect diagnostic information**
   ```bash
   # Run health check
   curl http://localhost:8000/health
   
   # Check versions
   python --version
   redis-cli --version
   docker --version
   ```

3. **Contact support**
   - Email: support@twistedmonk.com
   - Include: error messages, logs, configuration
   - Slack: #tech-support

4. **Community resources**
   - Documentation: https://docs.twistedmonk.com
   - GitHub Issues: https://github.com/your-org/twisted-monk-suite/issues
   - Stack Overflow: Tag `twisted-monk-suite`
