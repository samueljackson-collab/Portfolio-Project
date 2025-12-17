# Runbook — PRJ-WEB-001 (Commercial E-commerce & Booking Systems)

## Overview

Production operations runbook for Commercial E-commerce & Booking Systems - a portfolio of WordPress/WooCommerce-based websites including high-SKU flooring stores, resort booking systems, and tour operator platforms.

**System Components:**

- WordPress core with WooCommerce
- MySQL/MariaDB database (10,000+ products)
- PHP-FPM application server
- Nginx web server / Apache
- Redis object cache
- CDN for static assets
- Automated SQL import scripts for catalog updates
- Backup and monitoring systems

**Current Status:** 🔄 Recovery/Rebuild in Progress

**Original Deployments:**

- High-SKU Flooring Store (10,000+ products)
- Resort Booking Website
- Tour Operator Website

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Site availability** | 99.9% | Uptime monitoring (UptimeRobot, Pingdom) |
| **Page load time (TTFB)** | < 800ms | Time to first byte for product pages |
| **Checkout completion rate** | > 70% | Successful orders / cart initiations |
| **Database query time** | < 200ms | Average query execution time |
| **Product import success rate** | 99% | Successful imports / total import jobs |
| **Cache hit rate** | > 85% | Redis cache hits / total requests |
| **CDN cache hit rate** | > 90% | CDN hits / total static asset requests |

---

## Dashboards & Alerts

### Dashboards

#### Site Health Dashboard

```bash
# Check WordPress status
wp core version --path=/var/www/html
wp core check-update --path=/var/www/html

# Check WooCommerce status
wp wc status --path=/var/www/html

# Check plugin status
wp plugin list --path=/var/www/html --status=active

# Check for WordPress errors
tail -50 /var/www/html/wp-content/debug.log
```

#### Database Health Dashboard

```bash
# Check MySQL status
systemctl status mysql
mysqladmin -u root -p status

# Check database size
mysql -u root -p -e "
  SELECT table_schema AS 'Database',
         ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
  FROM information_schema.tables
  WHERE table_schema = 'woocommerce_db'
  GROUP BY table_schema;"

# Check slow queries
mysql -u root -p -e "SHOW GLOBAL STATUS LIKE 'Slow_queries';"

# Check table status
wp db check --path=/var/www/html
wp db optimize --path=/var/www/html --dry-run
```

#### Performance Dashboard

```bash
# Check PHP-FPM status
systemctl status php8.1-fpm
curl http://localhost/fpm-status

# Check Nginx/Apache status
systemctl status nginx
curl -I https://example.com

# Check Redis cache
redis-cli INFO stats | grep -E "hits|misses|memory"
redis-cli DBSIZE

# Monitor server resources
free -m
df -h
top -bn1 | head -20
```

#### E-commerce Metrics Dashboard

```bash
# Recent orders
wp wc order list --status=processing --path=/var/www/html | head -20

# Today's revenue
wp db query "
  SELECT SUM(meta_value) as daily_revenue
  FROM wp_postmeta
  WHERE meta_key = '_order_total'
  AND post_id IN (
    SELECT ID FROM wp_posts
    WHERE post_type = 'shop_order'
    AND DATE(post_date) = CURDATE()
  );" --path=/var/www/html

# Product stock alerts
wp wc product list --stock_status=lowstock --path=/var/www/html

# Failed payment attempts
wp db query "
  SELECT COUNT(*) as failed_payments
  FROM wp_posts
  WHERE post_type = 'shop_order'
  AND post_status = 'wc-failed'
  AND DATE(post_date) = CURDATE();" --path=/var/www/html
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Site completely down | Immediate | Check web server, database, PHP-FPM |
| **P0** | Database unavailable | Immediate | Restart MySQL, check for corruption |
| **P0** | Payment gateway down | Immediate | Contact gateway support, enable maintenance mode |
| **P1** | Page load time > 3s | 15 minutes | Check cache, database queries, CDN |
| **P1** | Product import failed | 15 minutes | Check import logs, validate data format |
| **P1** | High error rate (>5%) | 15 minutes | Check PHP errors, database errors |
| **P2** | Cache hit rate < 70% | 30 minutes | Warm cache, check Redis configuration |
| **P2** | Stock sync errors | 30 minutes | Check inventory management integration |
| **P2** | CDN purge needed | 30 minutes | Purge CDN cache for updated assets |
| **P3** | Single failed order | 1 hour | Investigate order, contact customer |

#### Alert Queries

```bash
# Check site availability
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://example.com)
if [ $HTTP_CODE -ne 200 ]; then
  echo "ALERT: Site returning HTTP $HTTP_CODE"
fi

# Check database connectivity
mysql -u wp_user -p$DB_PASSWORD -h localhost -e "SELECT 1" &>/dev/null
if [ $? -ne 0 ]; then
  echo "ALERT: Database connection failed"
fi

# Check disk space
DISK_USAGE=$(df -h /var/www | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
  echo "ALERT: Disk usage at ${DISK_USAGE}%"
fi

# Check PHP error rate
ERROR_COUNT=$(tail -1000 /var/www/html/wp-content/debug.log | grep -i "fatal\|error" | wc -l)
if [ $ERROR_COUNT -gt 50 ]; then
  echo "ALERT: High PHP error rate: $ERROR_COUNT errors in last 1000 log lines"
fi

# Check failed orders
FAILED_ORDERS=$(wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_type='shop_order' AND post_status='wc-failed' AND DATE(post_date)=CURDATE();" --path=/var/www/html --skip-column-names)
if [ $FAILED_ORDERS -gt 10 ]; then
  echo "ALERT: High failed order count: $FAILED_ORDERS today"
fi
```

---

## Standard Operations

### WordPress Site Management

#### Site Health Check

```bash
# WordPress core health
wp core verify-checksums --path=/var/www/html
wp core check-update --path=/var/www/html

# Database health
wp db check --path=/var/www/html

# Plugin and theme status
wp plugin list --path=/var/www/html --update=available
wp theme list --path=/var/www/html --update=available

# Security scan
wp plugin is-installed wordfence --path=/var/www/html && \
  wp wordfence scan --path=/var/www/html

# Performance check
wp cache flush --path=/var/www/html
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://example.com/
```

#### Update WordPress Core

```bash
# 1. Backup before update
/opt/scripts/backup-wordpress.sh

# 2. Enable maintenance mode
wp maintenance-mode activate --path=/var/www/html

# 3. Update core
wp core update --path=/var/www/html
wp core update-db --path=/var/www/html

# 4. Verify update
wp core version --path=/var/www/html
wp core verify-checksums --path=/var/www/html

# 5. Test site functionality
curl -I https://example.com
wp wc product list --path=/var/www/html | head -5

# 6. Disable maintenance mode
wp maintenance-mode deactivate --path=/var/www/html

# 7. Clear cache
wp cache flush --path=/var/www/html
# Purge CDN if applicable
```

#### Update Plugins

```bash
# Check for updates
wp plugin list --update=available --path=/var/www/html

# Backup before updating
/opt/scripts/backup-wordpress.sh

# Update specific plugin
wp plugin update woocommerce --path=/var/www/html

# Update all plugins
wp plugin update --all --path=/var/www/html

# Verify plugins active
wp plugin list --status=active --path=/var/www/html

# Check for errors
tail -50 /var/www/html/wp-content/debug.log
```

### WooCommerce Operations

#### Product Management

**Bulk Product Import:**

```bash
# Import products via CSV
wp wc product import /var/imports/products-$(date +%Y%m%d).csv \
  --path=/var/www/html \
  --user=admin

# Monitor import progress
tail -f /var/www/html/wp-content/uploads/wc-logs/product-import-$(date +Y-m-d)-*.log

# Verify import
wp wc product list --path=/var/www/html | wc -l

# Check for import errors
grep -i "error\|failed" /var/www/html/wp-content/uploads/wc-logs/product-import-*.log
```

**SQL-Based Price Update (High-SKU Store):**

```bash
# Prepare price update SQL
cat > /tmp/price-update.sql << 'EOF'
-- Backup current prices
CREATE TABLE IF NOT EXISTS wp_postmeta_backup_$(date +%Y%m%d) AS
SELECT * FROM wp_postmeta WHERE meta_key IN ('_regular_price', '_sale_price', '_price');

-- Update prices from staging table
-- (Assumes prices are in wp_price_updates table: product_sku, new_price)
UPDATE wp_postmeta pm
JOIN wp_posts p ON pm.post_id = p.ID
JOIN wp_postmeta pm_sku ON p.ID = pm_sku.post_id AND pm_sku.meta_key = '_sku'
JOIN wp_price_updates pu ON pm_sku.meta_value = pu.product_sku
SET pm.meta_value = pu.new_price
WHERE pm.meta_key = '_regular_price';

UPDATE wp_postmeta pm
JOIN wp_posts p ON pm.post_id = p.ID
JOIN wp_postmeta pm_sku ON p.ID = pm_sku.post_id AND pm_sku.meta_key = '_sku'
JOIN wp_price_updates pu ON pm_sku.meta_value = pu.product_sku
SET pm.meta_value = pu.new_price
WHERE pm.meta_key = '_price' AND pm.post_id NOT IN (
  SELECT post_id FROM wp_postmeta WHERE meta_key = '_sale_price'
);
EOF

# Test in staging environment first!
mysql -u root -p woocommerce_staging < /tmp/price-update.sql

# If successful, run in production
# 1. Create backup
mysqldump -u root -p woocommerce_db > /backup/db-pre-price-update-$(date +%Y%m%d).sql

# 2. Run update
mysql -u root -p woocommerce_db < /tmp/price-update.sql

# 3. Clear WooCommerce cache
wp wc tool run clear_transients --path=/var/www/html
wp cache flush --path=/var/www/html

# 4. Verify sample products
wp wc product get <product-id> --path=/var/www/html --field=price
```

**Product Stock Management:**

```bash
# Check low stock products
wp wc product list --stock_status=lowstock --path=/var/www/html

# Update stock for specific product
wp wc product update <product-id> --stock_quantity=100 --path=/var/www/html

# Bulk stock update via SQL (use with caution)
mysql -u root -p woocommerce_db << 'EOF'
UPDATE wp_postmeta
SET meta_value = 0
WHERE meta_key = '_stock_status'
AND meta_value = 'instock'
AND post_id IN (
  SELECT post_id FROM wp_postmeta
  WHERE meta_key = '_stock' AND CAST(meta_value AS SIGNED) <= 0
);
EOF

# Sync stock with external inventory system
/opt/scripts/sync-inventory.sh
```

#### Order Management

**View Recent Orders:**

```bash
# List orders
wp wc order list --status=processing --path=/var/www/html

# Get order details
wp wc order get <order-id> --path=/var/www/html

# Update order status
wp wc order update <order-id> --status=completed --path=/var/www/html

# Export orders for date range
wp wc order list --after="2025-01-01" --before="2025-01-31" \
  --format=csv --path=/var/www/html > /tmp/orders-jan-2025.csv
```

**Handle Failed Orders:**

```bash
# List failed orders
wp db query "
  SELECT ID, post_date, post_status
  FROM wp_posts
  WHERE post_type = 'shop_order'
  AND post_status = 'wc-failed'
  ORDER BY post_date DESC
  LIMIT 20;" --path=/var/www/html

# Investigate specific order
wp wc order get <order-id> --path=/var/www/html

# Check payment gateway logs
tail -100 /var/www/html/wp-content/uploads/wc-logs/payment-gateway-*.log

# Retry payment (if manual intervention needed)
# Contact customer or process manually through admin panel
```

### Database Operations

#### Database Backup

```bash
# Standard backup
mysqldump -u root -p woocommerce_db | gzip > \
  /backup/woocommerce-db-$(date +%Y%m%d-%H%M).sql.gz

# Backup with separate files per table
/opt/scripts/backup-db-by-table.sh woocommerce_db /backup/wc-tables-$(date +%Y%m%d)

# Backup specific tables (e.g., orders only)
mysqldump -u root -p woocommerce_db wp_posts wp_postmeta wp_woocommerce_order_items \
  wp_woocommerce_order_itemmeta | gzip > /backup/orders-$(date +%Y%m%d).sql.gz

# Automated daily backup via cron
cat > /etc/cron.daily/woocommerce-backup << 'EOF'
#!/bin/bash
mysqldump -u backup_user -p$DB_PASSWORD woocommerce_db | \
  gzip > /backup/daily/woocommerce-$(date +%Y%m%d).sql.gz
find /backup/daily -name "woocommerce-*.sql.gz" -mtime +30 -delete
EOF
chmod +x /etc/cron.daily/woocommerce-backup
```

#### Database Restore

```bash
# Restore full database
gunzip < /backup/woocommerce-db-20250101-1200.sql.gz | \
  mysql -u root -p woocommerce_db

# Restore specific tables
gunzip < /backup/orders-20250101.sql.gz | mysql -u root -p woocommerce_db

# Verify restoration
mysql -u root -p woocommerce_db -e "
  SELECT COUNT(*) as product_count FROM wp_posts WHERE post_type='product';
  SELECT COUNT(*) as order_count FROM wp_posts WHERE post_type='shop_order';
"

# Clear WordPress cache after restore
wp cache flush --path=/var/www/html
```

#### Database Optimization

```bash
# Check table status
wp db query "SHOW TABLE STATUS" --path=/var/www/html | grep -E "Rows|Data_length"

# Optimize tables
wp db optimize --path=/var/www/html

# Repair corrupted tables
wp db repair --path=/var/www/html

# Clean up revisions and trash
wp post delete $(wp post list --post_status=trash --format=ids --path=/var/www/html) \
  --force --path=/var/www/html

wp db query "DELETE FROM wp_posts WHERE post_type = 'revision'" --path=/var/www/html

# Clean up transients
wp transient delete --all --path=/var/www/html

# Clean up old sessions
mysql -u root -p woocommerce_db -e "
  DELETE FROM wp_woocommerce_sessions
  WHERE session_expiry < UNIX_TIMESTAMP() - 86400;
"
```

### Cache Management

#### Clear All Caches

```bash
# WordPress object cache
wp cache flush --path=/var/www/html

# WooCommerce transients
wp wc tool run clear_transients --path=/var/www/html

# Redis cache
redis-cli FLUSHALL

# Nginx cache (if using fastcgi_cache)
rm -rf /var/cache/nginx/*
systemctl reload nginx

# CDN cache (Cloudflare example)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'

# Verify cache cleared
curl -I https://example.com | grep -i "cache\|age"
```

#### Warm Cache

```bash
# Warm product pages
wp post list --post_type=product --format=ids --path=/var/www/html | \
while read id; do
  wp post get $id --path=/var/www/html > /dev/null
  curl -s "https://example.com/?p=$id" > /dev/null
done

# Warm category pages
wp term list product_cat --format=ids --path=/var/www/html | \
while read id; do
  SLUG=$(wp term get product_cat $id --field=slug --path=/var/www/html)
  curl -s "https://example.com/product-category/$SLUG/" > /dev/null
done

# Monitor cache hit rate
redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses"
```

### Booking System Operations (Resort/Tours)

#### Manage Bookings

```bash
# List today's bookings
wp db query "
  SELECT p.ID, p.post_title, pm.meta_value as booking_date
  FROM wp_posts p
  JOIN wp_postmeta pm ON p.ID = pm.post_id
  WHERE p.post_type = 'booking'
  AND pm.meta_key = 'booking_date'
  AND pm.meta_value = CURDATE()
  ORDER BY pm.meta_value;" --path=/var/www/html

# Check availability for date range
wp db query "
  SELECT DATE(meta_value) as date, COUNT(*) as bookings
  FROM wp_postmeta
  WHERE meta_key = 'booking_date'
  AND meta_value BETWEEN '2025-06-01' AND '2025-06-30'
  GROUP BY DATE(meta_value)
  ORDER BY date;" --path=/var/www/html

# Update booking status
wp post update <booking-id> --post_status=confirmed --path=/var/www/html

# Send booking confirmation
wp eval 'do_action("send_booking_confirmation", <booking-id>);' --path=/var/www/html
```

#### Capacity Management

```bash
# Check room/tour capacity for date
wp db query "
  SELECT resource_id, DATE(booking_date) as date,
         COUNT(*) as current_bookings, max_capacity
  FROM wp_bookings b
  JOIN wp_booking_resources r ON b.resource_id = r.id
  WHERE booking_date = '2025-06-15'
  GROUP BY resource_id, DATE(booking_date);" --path=/var/www/html

# Block dates for maintenance
wp post create --post_type=booking_block \
  --post_title="Maintenance Block" \
  --meta_input='{"start_date":"2025-07-01","end_date":"2025-07-07","resource_id":"5"}' \
  --path=/var/www/html
```

---

## Incident Response

### Detection

**Automated Detection:**

- UptimeRobot/Pingdom alerts
- Server monitoring (Nagios, Zabbix)
- Application performance monitoring (New Relic)
- Payment gateway webhooks for failures
- WooCommerce status emails

**Manual Detection:**

```bash
# Check site availability
curl -I https://example.com

# Check for WordPress errors
tail -50 /var/www/html/wp-content/debug.log

# Check web server errors
tail -50 /var/log/nginx/error.log
tail -50 /var/log/apache2/error.log

# Check database errors
tail -50 /var/log/mysql/error.log

# Check PHP errors
tail -50 /var/log/php8.1-fpm.log

# Check recent failed orders
wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_type='shop_order' AND post_status='wc-failed' AND DATE(post_date)=CURDATE();" --path=/var/www/html
```

### Triage

#### Severity Classification

### P0: Complete Outage

- Site completely unreachable (500/502/503 errors)
- Database server down
- Payment processing completely broken
- Data corruption detected

### P1: Major Degradation

- Site very slow (> 5s page load)
- Checkout process failing
- Product import failures affecting inventory
- High error rate (>10%)
- Email notifications not sending

### P2: Moderate Issues

- Individual page errors
- Cache performance degraded
- Stock sync delays
- Payment gateway intermittent issues
- CDN issues affecting static assets

### P3: Minor Issues

- Single order failure
- Image upload issues
- Minor plugin conflicts
- Low stock alerts

### Incident Response Procedures

#### P0: Site Completely Down

**Immediate Actions (0-2 minutes):**

```bash
# 1. Check web server status
systemctl status nginx
# or
systemctl status apache2

# 2. Check PHP-FPM
systemctl status php8.1-fpm

# 3. Check MySQL
systemctl status mysql

# 4. Check quick errors
tail -20 /var/log/nginx/error.log
tail -20 /var/www/html/wp-content/debug.log
```

**Investigation (2-10 minutes):**

```bash
# Check system resources
free -m
df -h
top -bn1 | head -20

# Check for process issues
ps aux | grep -E "nginx|php-fpm|mysql" | grep -v grep

# Check database connectivity
mysql -u wp_user -p$DB_PASSWORD -e "SELECT 1"

# Check WordPress database
wp db check --path=/var/www/html

# Check for plugin/theme conflicts
wp plugin list --status=active --path=/var/www/html
tail -100 /var/www/html/wp-content/debug.log | grep -i "fatal"
```

**Mitigation:**

```bash
# Option 1: Restart services
systemctl restart nginx
systemctl restart php8.1-fpm
systemctl restart mysql

# Option 2: Enable maintenance mode and investigate
wp maintenance-mode activate --path=/var/www/html

# Option 3: Disable problematic plugins
wp plugin deactivate <plugin-name> --path=/var/www/html

# Option 4: Restore from backup (if corruption suspected)
gunzip < /backup/woocommerce-db-latest.sql.gz | mysql -u root -p woocommerce_db

# Verify site recovery
curl -I https://example.com
wp maintenance-mode deactivate --path=/var/www/html
```

#### P1: Checkout Process Failing

**Investigation:**

```bash
# Check WooCommerce status
wp wc status --path=/var/www/html

# Check payment gateway logs
tail -100 /var/www/html/wp-content/uploads/wc-logs/payment-*.log

# Check recent failed orders
wp db query "
  SELECT ID, post_date, post_status
  FROM wp_posts
  WHERE post_type = 'shop_order'
  AND post_status = 'wc-failed'
  AND post_date > DATE_SUB(NOW(), INTERVAL 1 HOUR);" --path=/var/www/html

# Check for JavaScript errors
# Review browser console in checkout page

# Test checkout manually
# Attempt test order in staging environment
```

**Mitigation:**

```bash
# Disable problematic payment gateway
wp wc payment_gateway update <gateway-id> --enabled=false --path=/var/www/html

# Enable fallback payment method
wp wc payment_gateway update cod --enabled=true --path=/var/www/html

# Clear checkout cache
wp cache flush --path=/var/www/html
wp wc tool run clear_transients --path=/var/www/html

# Notify customers
# Send email about temporary payment issues and alternative methods

# Contact payment gateway support
# Open support ticket with payment provider

# Monitor order completion rate
watch -n 30 'wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_type=\"shop_order\" AND post_status=\"wc-processing\" AND DATE(post_date)=CURDATE();" --path=/var/www/html'
```

#### P1: Product Import Failed

**Investigation:**

```bash
# Check import logs
tail -100 /var/www/html/wp-content/uploads/wc-logs/product-import-*.log

# Check source file
head -50 /var/imports/products-$(date +%Y%m%d).csv
wc -l /var/imports/products-$(date +%Y%m%d).csv

# Validate CSV format
csvvalidate /var/imports/products-$(date +%Y%m%d).csv

# Check database for partial import
wp wc product list --path=/var/www/html | wc -l

# Check for database errors
tail -50 /var/log/mysql/error.log
```

**Mitigation:**

```bash
# Fix CSV format issues
# Clean data in source file

# Rollback partial import if needed
mysql -u root -p woocommerce_db << 'EOF'
DELETE FROM wp_posts
WHERE post_type = 'product'
AND post_date > DATE_SUB(NOW(), INTERVAL 1 HOUR);
EOF

# Re-run import with fixed data
wp wc product import /var/imports/products-$(date +%Y%m%d)-fixed.csv \
  --path=/var/www/html \
  --user=admin

# Verify import success
wp wc product list --path=/var/www/html | wc -l

# Clear cache
wp cache flush --path=/var/www/html
```

#### P2: Site Performance Degraded

**Investigation:**

```bash
# Check page load time
time curl -o /dev/null -s https://example.com/shop/

# Check database slow queries
mysql -u root -p -e "SHOW FULL PROCESSLIST;"

# Check for long-running queries
mysql -u root -p -e "
  SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST
  WHERE COMMAND != 'Sleep' AND TIME > 5
  ORDER BY TIME DESC;"

# Check server resources
top -bn1 | head -20
iostat -x 1 5

# Check cache hit rate
redis-cli INFO stats | grep -E "hits|misses"
```

**Mitigation:**

```bash
# Clear and rebuild cache
wp cache flush --path=/var/www/html
redis-cli FLUSHALL

# Warm cache
/opt/scripts/warm-cache.sh

# Optimize database
wp db optimize --path=/var/www/html

# Kill long-running queries
mysql -u root -p -e "KILL <process-id>;"

# Enable CDN if not already
# Update DNS to point to CDN

# Scale resources if needed
# Increase PHP-FPM workers, MySQL resources
```

### Post-Incident

**After Resolution:**

```bash
# Document incident
cat > /var/log/incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report - WooCommerce Site

**Date:** $(date)
**Severity:** P1
**Duration:** 35 minutes
**Affected Component:** Product import system

## Timeline
- 09:00: Weekly product price update initiated
- 09:10: Import failed with database errors
- 09:15: Identified malformed CSV with invalid UTF-8 characters
- 09:20: Cleaned CSV and rolled back partial import
- 09:25: Re-ran import successfully
- 09:35: Verified all products updated, cache cleared

## Root Cause
Source data contained invalid UTF-8 characters causing MySQL import errors

## Action Items
- [ ] Add CSV validation step before import
- [ ] Implement automatic character encoding detection
- [ ] Add rollback automation for failed imports
- [ ] Update import documentation

EOF

# Update incident log
echo "$(date +%Y-%m-%d),P1,35,product-import" >> /var/log/incidents/incident-log.csv
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Site Issues

```bash
# Check WordPress install
wp core verify-checksums --path=/var/www/html
wp db check --path=/var/www/html

# Check for conflicts
wp plugin list --status=active --path=/var/www/html
wp theme list --status=active --path=/var/www/html

# Check error logs
tail -100 /var/www/html/wp-content/debug.log
tail -100 /var/log/nginx/error.log
tail -100 /var/log/php8.1-fpm.log

# Test site response
curl -I https://example.com
curl -o /dev/null -s -w "Time: %{time_total}s, HTTP: %{http_code}\n" https://example.com
```

#### Database Issues

```bash
# Check database connectivity
mysql -u wp_user -p$DB_PASSWORD -e "SELECT 1"

# Check database size and tables
mysql -u root -p woocommerce_db -e "SHOW TABLE STATUS;"

# Check for table corruption
wp db check --path=/var/www/html

# Repair tables if needed
wp db repair --path=/var/www/html

# Check slow queries
mysql -u root -p -e "SHOW FULL PROCESSLIST;"
```

#### Performance Issues

```bash
# Check server load
uptime
top -bn1 | head -20

# Check disk usage
df -h
du -sh /var/www/html/*

# Check memory usage
free -m

# Check cache performance
redis-cli INFO stats
redis-cli MONITOR  # Watch cache activity (Ctrl+C to stop)

# Check PHP-FPM pool
systemctl status php8.1-fpm
cat /var/log/php8.1-fpm.log | grep "pool www" | tail -20
```

### Common Issues & Solutions

#### Issue: "White Screen of Death (WSOD)"

**Symptoms:**

- Blank white page
- No error messages visible
- Site completely unresponsive

**Diagnosis:**

```bash
# Enable WP_DEBUG
wp config set WP_DEBUG true --path=/var/www/html
wp config set WP_DEBUG_LOG true --path=/var/www/html

# Check debug log
tail -50 /var/www/html/wp-content/debug.log

# Check PHP error log
tail -50 /var/log/php8.1-fpm.log

# Check for fatal errors
grep -i "fatal" /var/www/html/wp-content/debug.log
```

**Solution:**

```bash
# Disable plugins one by one
wp plugin deactivate --all --path=/var/www/html

# Test site
curl -I https://example.com

# Reactivate plugins one by one
for plugin in $(wp plugin list --status=inactive --field=name --path=/var/www/html); do
  wp plugin activate $plugin --path=/var/www/html
  echo "Activated: $plugin - Test site now"
  sleep 5
done

# If theme issue, switch to default theme
wp theme activate twentytwentyfour --path=/var/www/html

# Increase PHP memory limit if needed
wp config set WP_MEMORY_LIMIT 256M --path=/var/www/html
```

---

#### Issue: "Database connection error"

**Symptoms:**

- "Error establishing database connection"
- Site completely down
- Cannot access admin panel

**Diagnosis:**

```bash
# Check MySQL status
systemctl status mysql

# Check database credentials
wp config get DB_NAME DB_USER --path=/var/www/html

# Test database connection
mysql -u $(wp config get DB_USER --path=/var/www/html) \
      -p$(wp config get DB_PASSWORD --path=/var/www/html) \
      -h $(wp config get DB_HOST --path=/var/www/html) \
      -e "SELECT 1"

# Check MySQL error log
tail -50 /var/log/mysql/error.log
```

**Solution:**

```bash
# Restart MySQL
systemctl restart mysql

# Check and repair tables
wp db check --path=/var/www/html
wp db repair --path=/var/www/html

# Restore from backup if corrupted
gunzip < /backup/woocommerce-db-latest.sql.gz | \
  mysql -u root -p woocommerce_db

# Update wp-config.php if credentials changed
wp config set DB_USER new_username --path=/var/www/html
wp config set DB_PASSWORD new_password --path=/var/www/html
```

---

#### Issue: "Products not displaying correctly after import"

**Symptoms:**

- Missing product images
- Incorrect prices
- Missing attributes
- Broken product links

**Diagnosis:**

```bash
# Check import log
tail -100 /var/www/html/wp-content/uploads/wc-logs/product-import-*.log

# Check product data
wp wc product list --path=/var/www/html | head -20

# Check specific product
wp wc product get <product-id> --path=/var/www/html

# Check for missing images
wp db query "
  SELECT COUNT(*)
  FROM wp_posts p
  LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_thumbnail_id'
  WHERE p.post_type = 'product'
  AND (pm.meta_value IS NULL OR pm.meta_value = '');" --path=/var/www/html
```

**Solution:**

```bash
# Regenerate product permalinks
wp rewrite flush --path=/var/www/html

# Clear product cache
wp wc tool run clear_transients --path=/var/www/html
wp cache flush --path=/var/www/html

# Regenerate product images
wp media regenerate --yes --path=/var/www/html

# Fix missing prices (run carefully)
mysql -u root -p woocommerce_db << 'EOF'
UPDATE wp_postmeta pm
SET pm.meta_value = (
  SELECT meta_value
  FROM wp_postmeta
  WHERE post_id = pm.post_id
  AND meta_key = '_regular_price'
  LIMIT 1
)
WHERE pm.meta_key = '_price'
AND pm.post_id IN (SELECT ID FROM wp_posts WHERE post_type = 'product')
AND pm.meta_value = '';
EOF
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 24 hours (daily backups)
- **RTO** (Recovery Time Objective): 2 hours (site restoration)

### Backup Strategy

**Automated Daily Backups:**

```bash
# Full site backup script
cat > /opt/scripts/backup-wordpress.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/woocommerce"
DATE=$(date +%Y%m%d-%H%M)

mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u backup_user -p$DB_PASSWORD woocommerce_db | \
  gzip > $BACKUP_DIR/db-$DATE.sql.gz

# Backup WordPress files
tar -czf $BACKUP_DIR/wp-files-$DATE.tar.gz /var/www/html

# Backup uploads only (faster for frequent backups)
tar -czf $BACKUP_DIR/wp-uploads-$DATE.tar.gz /var/www/html/wp-content/uploads

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Upload to S3 or remote storage
# aws s3 sync $BACKUP_DIR s3://my-backups/woocommerce/

echo "Backup completed: $DATE"
EOF

chmod +x /opt/scripts/backup-wordpress.sh

# Schedule daily backup
(crontab -l; echo "0 2 * * * /opt/scripts/backup-wordpress.sh") | crontab -
```

**Off-site Backups:**

```bash
# Sync to remote server
rsync -avz /backup/woocommerce/ user@remote-server:/backups/woocommerce/

# Or sync to S3
aws s3 sync /backup/woocommerce/ s3://my-bucket/woocommerce-backups/

# Or use BackupBuddy/UpdraftPlus plugin
wp plugin install updraftplus --activate --path=/var/www/html
```

### Disaster Recovery Procedures

#### Full Site Recovery

```bash
# 1. Restore database
gunzip < /backup/woocommerce/db-latest.sql.gz | \
  mysql -u root -p woocommerce_db

# 2. Restore WordPress files
cd /var/www
tar -xzf /backup/woocommerce/wp-files-latest.tar.gz

# 3. Set correct permissions
chown -R www-data:www-data /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;

# 4. Verify wp-config.php
cat /var/www/html/wp-config.php | grep DB_

# 5. Test database connection
wp db check --path=/var/www/html

# 6. Clear cache
wp cache flush --path=/var/www/html

# 7. Test site
curl -I https://example.com

# 8. Verify admin access
curl -I https://example.com/wp-admin/

# 9. Verify products
wp wc product list --path=/var/www/html | head -10
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks

```bash
# Check site health
curl -I https://example.com
wp core check-update --path=/var/www/html

# Check for errors
tail -20 /var/www/html/wp-content/debug.log | grep -i "error\|fatal"

# Check failed orders
wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_type='shop_order' AND post_status='wc-failed' AND DATE(post_date)=CURDATE();" --path=/var/www/html

# Check backups
ls -lh /backup/woocommerce/ | tail -5

# Monitor disk space
df -h /var/www
```

#### Weekly Tasks

```bash
# Update plugins and themes
wp plugin update --all --path=/var/www/html
wp theme update --all --path=/var/www/html

# Optimize database
wp db optimize --path=/var/www/html

# Clear old transients
wp transient delete --all --path=/var/www/html

# Review slow queries
# Check MySQL slow query log

# Generate reports
wp wc report sales --period=week --path=/var/www/html
```

#### Monthly Tasks

```bash
# Update WordPress core
wp core update --path=/var/www/html

# Security audit
wp plugin list --update=available --path=/var/www/html
wp plugin list --status=inactive --path=/var/www/html  # Consider removing unused plugins

# Clean up database
wp db query "DELETE FROM wp_posts WHERE post_type='revision' AND post_date < DATE_SUB(NOW(), INTERVAL 90 DAY);" --path=/var/www/html
wp db optimize --path=/var/www/html

# Review and archive old orders
# Export orders older than 2 years for archival

# Test backups
# Restore to staging environment and verify

# Capacity planning
# Review disk usage, traffic trends, database growth
```

---

## Recovery/Rebuild Operations

**Note:** Since this project is in recovery status, these procedures document the rebuild process.

### Data Recovery from Lost Systems

#### Export Available Data

```bash
# If partial database backups exist
gunzip < /recovery/partial-db-backup.sql.gz | mysql -u root -p recovery_db

# Export salvageable product data
mysql -u root -p recovery_db -e "
  SELECT p.ID, p.post_title, p.post_name,
         GROUP_CONCAT(CONCAT(pm.meta_key, ':', pm.meta_value) SEPARATOR '|') as meta_data
  FROM wp_posts p
  LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id
  WHERE p.post_type = 'product'
  GROUP BY p.ID
  ORDER BY p.post_title;" > /recovery/products-export.tsv

# Export order data if available
mysql -u root -p recovery_db -e "
  SELECT * FROM wp_posts
  WHERE post_type = 'shop_order'
  ORDER BY post_date DESC;" > /recovery/orders-export.tsv

# Document database schema
mysqldump -u root -p recovery_db --no-data > /recovery/schema-export.sql
```

#### Rebuild Documentation

```bash
# Document recovered workflows
cat > /recovery/docs/catalog-update-workflow.md << 'EOF'
# Catalog Update Workflow (Reconstructed from Memory)

## Weekly Price Update Process

1. Receive supplier price CSV via email
2. Validate CSV format and data integrity
3. Upload to staging database
4. Run SQL update script:
   - Backup current prices
   - Update products by SKU
   - Validate price changes
5. Test sample products in staging
6. Deploy to production during maintenance window
7. Clear caches (Redis, CDN)
8. Verify product pages

## SQL Update Script Template

[SQL script reconstructed from memory - see price-update-template.sql]
EOF

# Create sanitized code examples
# Document architecture decisions
# Capture lessons learned
```

---

## Operational Best Practices

### Pre-Deployment Checklist

- [ ] Full backup completed
- [ ] Changes tested in staging environment
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Maintenance window scheduled
- [ ] Stakeholders notified

### Post-Deployment Checklist

- [ ] Site loads correctly
- [ ] Checkout process tested
- [ ] Product pages display correctly
- [ ] No errors in logs
- [ ] Cache cleared and warmed
- [ ] Performance metrics normal
- [ ] Monitor for 1 hour

---

## Quick Reference Card

### Most Common Operations

```bash
# Check site health
wp core verify-checksums --path=/var/www/html
curl -I https://example.com

# Clear all caches
wp cache flush --path=/var/www/html
wp wc tool run clear_transients --path=/var/www/html
redis-cli FLUSHALL

# Backup database
mysqldump -u root -p woocommerce_db | gzip > /backup/db-$(date +%Y%m%d).sql.gz

# Update WordPress
wp core update --path=/var/www/html
wp plugin update --all --path=/var/www/html

# Optimize database
wp db optimize --path=/var/www/html

# View recent orders
wp wc order list --status=processing --path=/var/www/html
```

### Emergency Response

```bash
# P0: Site down
systemctl restart nginx
systemctl restart php8.1-fpm
systemctl restart mysql

# P1: Checkout failing
wp plugin deactivate <problematic-plugin> --path=/var/www/html
wp cache flush --path=/var/www/html

# P2: Performance issues
wp cache flush --path=/var/www/html
wp db optimize --path=/var/www/html
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Web Development & Data Management Team
- **Review Schedule:** Quarterly or after major changes
- **Status:** Recovery documentation - subject to updates as systems are rebuilt
- **Feedback:** Create issue or submit PR with updates
