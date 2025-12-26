# Architecture & ERD (Sanitized)

```mermaid
graph TD
  subgraph Web
    CDN[CDN/Edge Cache]
    NGINX[Nginx/Apache]
    PHP[PHP-FPM + WordPress/WooCommerce]
  end

  subgraph Data
    DB[(MariaDB/MySQL)]
    CACHE[Redis Object Cache]
  end

  subgraph Workers
    ETL[Catalog ETL Jobs]
    VALIDATE[Validation Jobs]
    BACKUP[Backup Automation]
  end

  USERS[Site Visitors]
  ADMINS[Content/Admin Users]

  USERS -->|HTTPS| CDN --> NGINX --> PHP --> DB
  PHP --> CACHE
  ADMINS -->|WP-Admin| NGINX
  ETL --> DB
  VALIDATE --> DB
  BACKUP --> DB
  ETL --> CACHE
  VALIDATE --> CACHE
```

### ERD Highlights (Textual)
- `catalog_products` (PK: `product_id`) — base product metadata; joins to `catalog_prices` (FK: `product_id`) and `catalog_inventory` (FK: `product_id`).
- `catalog_prices` — seasonal pricing with `effective_from`/`effective_to`; enforced uniqueness on `(product_id, effective_from)`.
- `catalog_inventory` — stock ledger with `stock_qty` and `reorder_threshold`.
- `catalog_media` — references sanitized filenames and alt text for SEO; FK to `catalog_products`.
- `booking_reservations` — booking headers; joins `booking_units` (inventory) and `booking_rate_rules` (pricing logic); audit trail in `booking_events`.
- `ops_jobs` & `ops_validations` — operational logging for imports, backups, and validation runs.
