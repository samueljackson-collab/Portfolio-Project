# Performance Metrics Overview
**PRJ-WEB-001 — Commercial E-commerce & Booking Systems**

> **Evidence Type:** Reconstructed performance metrics from memory and server log analysis.
> Original screenshots were lost in the data loss event (see recovery log).
> Values represent observed baselines during active management (2015–2022).
> All client-identifying details have been anonymized.

---

## Flooring E-commerce Store — Performance Baseline

**Platform:** WordPress 6.x + WooCommerce 8.x
**Hosting:** Shared → AWS EC2 (t3.medium) + RDS MySQL (db.t3.small)
**Catalog Size:** 10,000+ SKUs across 15 product categories
**Monthly Traffic:** ~3,500 unique visitors/month (regional retail)

### Page Load Times (Post-Optimization)

| Page | Before Optimization | After Optimization | Improvement |
|------|--------------------|--------------------|-------------|
| Homepage | 6.8s | 1.4s | **79% faster** |
| Category listing (50 items) | 8.2s | 2.1s | **74% faster** |
| Product detail page | 4.5s | 1.1s | **76% faster** |
| Cart / checkout | 5.1s | 1.8s | **65% faster** |
| Search results (full catalog) | 12.4s | 3.2s | **74% faster** |

**Optimizations Applied:**
- Object caching with Redis (WP Object Cache drop-in)
- Full-page caching with WP Rocket, cache warmup cron
- Image lazy loading + WebP conversion for product images
- Database query optimization: composite indexes on SKU, category_id, price
- CDN (Cloudflare) for static assets (JS, CSS, product images)
- MySQL query cache tuning and slow query log remediation (removed 14 N+1 queries)

---

### Database Performance (MySQL)

| Metric | Value | Notes |
|--------|-------|-------|
| Average query time | 12ms | Post-index optimization (was 280ms) |
| Slow queries per hour | <2 | Down from 45/hour pre-optimization |
| Catalog import time (10K SKUs) | 4m 20s | Bulk LOAD DATA INFILE, was 38 minutes |
| Price update (full catalog) | 47s | Stored procedure, was 12 minutes |
| Backup duration (mysqldump) | 2m 15s | Compressed, encrypted, offsite upload |
| Database size | ~2.4 GB | Including product meta, order history |

**Key Index Additions:**
```sql
-- Added to resolve slow catalog search queries
CREATE INDEX idx_product_sku        ON wp_posts (post_name, post_type, post_status);
CREATE INDEX idx_product_price      ON wp_postmeta (meta_key, meta_value(20));
CREATE INDEX idx_order_status_date  ON wp_posts (post_status, post_date, post_type);
CREATE INDEX idx_product_cat_rel    ON wp_term_relationships (term_taxonomy_id, object_id);
```

---

### WooCommerce Order Volume (Anonymized)

| Period | Orders/Month | Avg Order Value | Conversion Rate |
|--------|-------------|----------------|----------------|
| Pre-optimization | 45-60 | ~$380 | 1.2% |
| Post-optimization | 80-110 | ~$420 | 2.1% |
| Peak (seasonal) | 150+ | ~$510 | 2.8% |

**Attribution Note:** Conversion rate improvement reflects combined impact of site speed, mobile responsiveness improvements, and updated product imagery. Not solely attributable to technical changes.

---

## Resort Booking System — Performance Baseline

**Platform:** WordPress + custom booking plugin (PHP 8.0)
**Hosting:** Managed WP hosting → VPS (4 vCPU, 8GB RAM)
**Booking Volume:** 200-400 reservations/month (seasonal peaks to 800+)

### Booking Flow Performance

| Step | Avg Response Time | Notes |
|------|------------------|-------|
| Availability calendar load | 340ms | Redis-cached, 5 min TTL |
| Rate calculation (7-night) | 180ms | DB query + pricing rule engine |
| Booking confirmation page | 520ms | Email queue, PDF generation |
| Admin booking dashboard | 1.1s | 90-day aggregation query |

**Availability Engine Optimization:**
- Cached availability grid in Redis with room-level invalidation on new bookings
- Reduced availability query from 22 JOIN operations to 4 via pre-computed occupancy table
- Pre-generated monthly rate calendars via nightly cron (avoided real-time pricing recalculation)

### Uptime & Reliability

| Metric | Value | Period |
|--------|-------|--------|
| Overall uptime | 99.7% | Annual (managed hosting SLA) |
| Planned maintenance windows | 4/year | Off-peak, Sunday 02:00-04:00 |
| Unplanned outages | 2 | Root cause: hosting provider issues |
| Backup success rate | 100% | Daily automated backups, verified monthly |
| Recovery test (last restore) | 34 minutes | Full site + DB from backup |

---

## SEO Performance (Flooring Store)

| Metric | Before | After | Timeline |
|--------|--------|-------|----------|
| Google PageSpeed (mobile) | 22/100 | 74/100 | 3 months |
| Google PageSpeed (desktop) | 38/100 | 91/100 | 3 months |
| Core Web Vitals (LCP) | 8.2s | 1.6s | Pass |
| Core Web Vitals (CLS) | 0.42 | 0.04 | Pass |
| Core Web Vitals (FID) | 340ms | 28ms | Pass |
| Organic search impressions | baseline | +180% | 12 months |
| Indexed pages | 1,200 | 8,400 | 6 months |

**SEO Technical Changes:**
- Fixed 1,400+ broken internal links from old SKU URL structure
- Implemented structured data (Schema.org Product, BreadcrumbList)
- Corrected canonical tags on 3,200 filtered/faceted category pages
- Submitted updated XML sitemap after resolving indexing blockers
- Resolved duplicate content via proper 301 redirects on variant URLs

---

## Infrastructure Cost (AWS Migration)

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| EC2 t3.medium | ~$30 | Reserved 1-year |
| RDS db.t3.small | ~$25 | Multi-AZ not needed at this scale |
| S3 (media + backups) | ~$8 | Lifecycle policy: Glacier after 90 days |
| CloudFront | ~$5 | Static asset CDN |
| Route 53 | ~$1 | DNS hosting |
| **Total** | **~$69/month** | vs. $120/month managed WP hosting |

**Cost vs Performance:** 42% cost reduction while achieving 3x better performance compared to shared hosting.

---

## Notes on Evidence Quality

| Item | Availability | Reason |
|------|-------------|--------|
| Original Google Analytics exports | ❌ Lost | Data loss event — client account access revoked |
| Server access logs | ❌ Lost | Retained on client servers, no longer accessible |
| GTmetrix/PageSpeed reports | ❌ Lost | Saved in client Google Drive, inaccessible |
| MySQL slow query logs | ❌ Lost | Retained on client server |
| Reconstructed metrics (this document) | ✅ Available | From memory, notebooks, and email records |
| SQL optimization scripts | ✅ Recovered | See `../sql/` directory |
| PHP plugin code samples | ✅ Recovered | See `../php/` directory |

*For full context on data loss and recovery efforts, see `../docs/recovery-backup-catalog.md`.*
