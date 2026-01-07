-- PostgreSQL Target Database Initialization
-- Schema compatible with MySQL source for cross-database migration

-- Create custom types to match MySQL ENUMs
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user', 'guest');
CREATE TYPE product_category AS ENUM ('electronics', 'clothing', 'food', 'books', 'toys', 'other');
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded');
CREATE TYPE payment_status AS ENUM ('unpaid', 'paid', 'refunded', 'failed');
CREATE TYPE payment_method AS ENUM ('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash');
CREATE TYPE inventory_change_type AS ENUM ('purchase', 'sale', 'adjustment', 'return', 'damaged');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    status user_status DEFAULT 'active',
    role user_role DEFAULT 'user',
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category product_category NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    weight_kg DECIMAL(8, 3),
    is_active BOOLEAN DEFAULT TRUE,
    attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status order_status DEFAULT 'pending',
    payment_status payment_status DEFAULT 'unpaid',
    payment_method payment_method DEFAULT 'credit_card',
    subtotal DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0.00,
    shipping_amount DECIMAL(10, 2) DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    shipping_address JSONB,
    billing_address JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    line_total DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Create inventory_log table
CREATE TABLE IF NOT EXISTS inventory_log (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    change_type inventory_change_type NOT NULL,
    quantity_change INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    reference_id BIGINT,
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_log_product_id ON inventory_log(product_id);
CREATE INDEX idx_inventory_log_change_type ON inventory_log(change_type);
CREATE INDEX idx_inventory_log_created_at ON inventory_log(created_at);

-- Create migration_tracking table for monitoring
CREATE TABLE IF NOT EXISTS migration_tracking (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(100) NOT NULL,
    last_synced_id BIGINT,
    last_synced_at TIMESTAMP,
    rows_migrated BIGINT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_migration_tracking_updated_at BEFORE UPDATE ON migration_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable logical replication for CDC from this database
ALTER TABLE users REPLICA IDENTITY FULL;
ALTER TABLE products REPLICA IDENTITY FULL;
ALTER TABLE orders REPLICA IDENTITY FULL;
ALTER TABLE order_items REPLICA IDENTITY FULL;
ALTER TABLE inventory_log REPLICA IDENTITY FULL;

-- Create validation functions
CREATE OR REPLACE FUNCTION validate_migration_counts(
    source_users INT, source_products INT, source_orders INT, source_items INT
) RETURNS TABLE (
    table_name VARCHAR,
    source_count INT,
    target_count BIGINT,
    match BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'users'::VARCHAR, source_users, COUNT(*)::BIGINT, COUNT(*) = source_users FROM users
    UNION ALL
    SELECT 'products'::VARCHAR, source_products, COUNT(*)::BIGINT, COUNT(*) = source_products FROM products
    UNION ALL
    SELECT 'orders'::VARCHAR, source_orders, COUNT(*)::BIGINT, COUNT(*) = source_orders FROM orders
    UNION ALL
    SELECT 'order_items'::VARCHAR, source_items, COUNT(*)::BIGINT, COUNT(*) = source_items FROM order_items;
END;
$$ LANGUAGE plpgsql;

-- Display initialization message
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL Target Database Initialized';
    RAISE NOTICE 'Tables created: users, products, orders, order_items, inventory_log, migration_tracking';
    RAISE NOTICE 'Ready to receive migrated data from MySQL source';
END $$;
