-- Additional indexes and constraints for performance tuning

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_new_total_amount ON orders_new(total_amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_new_status_created_at ON orders_new(status, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_new_last_login ON users_new(last_login_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_new_inventory_count ON products_new(inventory_count);
