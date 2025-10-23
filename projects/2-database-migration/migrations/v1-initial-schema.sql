-- Zero-downtime migration: Create new tables alongside old ones

-- Users table with improved schema
CREATE TABLE IF NOT EXISTS users_new (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_new_email ON users_new(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_new_created_at ON users_new(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_new_active ON users_new(is_active) WHERE is_active = TRUE;

CREATE TABLE IF NOT EXISTS orders_new (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users_new(id)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_new_user_id ON orders_new(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_new_status ON orders_new(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_new_created_at ON orders_new(created_at);

CREATE TABLE IF NOT EXISTS products_new (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    inventory_count INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_new_sku ON products_new(sku);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_new_available ON products_new(is_available) WHERE is_available = TRUE;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_new_price ON products_new(price);
