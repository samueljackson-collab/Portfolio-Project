-- Initialize source database with sample data for migration demo

-- Create sample tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Insert sample data
INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com'),
    ('david', 'david@example.com'),
    ('eve', 'eve@example.com'),
    ('frank', 'frank@example.com'),
    ('grace', 'grace@example.com'),
    ('henry', 'henry@example.com'),
    ('iris', 'iris@example.com'),
    ('jack', 'jack@example.com');

INSERT INTO products (name, description, price, stock_quantity) VALUES
    ('Laptop', 'High-performance laptop', 1299.99, 50),
    ('Mouse', 'Wireless mouse', 29.99, 200),
    ('Keyboard', 'Mechanical keyboard', 89.99, 150),
    ('Monitor', '27-inch 4K monitor', 449.99, 75),
    ('Headphones', 'Noise-cancelling headphones', 199.99, 100),
    ('Webcam', '1080p webcam', 79.99, 120),
    ('Desk Lamp', 'LED desk lamp', 39.99, 180),
    ('USB Cable', 'USB-C cable', 12.99, 500),
    ('Phone Stand', 'Adjustable phone stand', 19.99, 300),
    ('Laptop Bag', 'Protective laptop bag', 59.99, 90);

-- Insert sample orders
INSERT INTO orders (user_id, order_number, total_amount, status) VALUES
    (1, 'ORD-2024-0001', 1329.98, 'completed'),
    (2, 'ORD-2024-0002', 539.97, 'completed'),
    (3, 'ORD-2024-0003', 89.99, 'pending'),
    (4, 'ORD-2024-0004', 1799.96, 'shipped'),
    (5, 'ORD-2024-0005', 229.98, 'processing'),
    (6, 'ORD-2024-0006', 449.99, 'completed'),
    (7, 'ORD-2024-0007', 119.98, 'pending'),
    (8, 'ORD-2024-0008', 679.96, 'shipped'),
    (9, 'ORD-2024-0009', 32.98, 'completed'),
    (10, 'ORD-2024-0010', 159.98, 'processing');

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 1, 29.99),
    (2, 4, 1, 449.99),
    (2, 3, 1, 89.99),
    (3, 3, 1, 89.99),
    (4, 1, 1, 1299.99),
    (4, 5, 1, 199.99),
    (4, 6, 1, 79.99),
    (4, 7, 1, 39.99),
    (5, 5, 1, 199.99),
    (5, 2, 1, 29.99),
    (6, 4, 1, 449.99),
    (7, 6, 1, 79.99),
    (7, 7, 1, 39.99),
    (8, 1, 1, 1299.99),
    (8, 3, 1, 89.99),
    (8, 8, 10, 12.99),
    (8, 9, 2, 19.99),
    (9, 8, 2, 12.99),
    (9, 7, 1, 39.99),
    (10, 6, 2, 79.99);

-- Create a function to simulate ongoing writes (for CDC testing)
CREATE OR REPLACE FUNCTION simulate_writes()
RETURNS void AS $$
BEGIN
    -- Insert a new order
    INSERT INTO orders (user_id, order_number, total_amount, status)
    VALUES (
        (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
        'ORD-' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD-HH24MISS'),
        ROUND((RANDOM() * 1000)::numeric, 2),
        (ARRAY['pending', 'processing', 'shipped', 'completed'])[FLOOR(RANDOM() * 4 + 1)]
    );

    -- Update a random order status
    UPDATE orders
    SET status = (ARRAY['pending', 'processing', 'shipped', 'completed'])[FLOOR(RANDOM() * 4 + 1)],
        updated_at = CURRENT_TIMESTAMP
    WHERE id = (SELECT id FROM orders ORDER BY RANDOM() LIMIT 1);
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions for replication
ALTER TABLE users REPLICA IDENTITY FULL;
ALTER TABLE orders REPLICA IDENTITY FULL;
ALTER TABLE products REPLICA IDENTITY FULL;
ALTER TABLE order_items REPLICA IDENTITY FULL;

-- Create publication for logical replication
CREATE PUBLICATION dbz_publication FOR ALL TABLES;

-- Display summary
DO $$
DECLARE
    user_count INTEGER;
    product_count INTEGER;
    order_count INTEGER;
    order_item_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO product_count FROM products;
    SELECT COUNT(*) INTO order_count FROM orders;
    SELECT COUNT(*) INTO order_item_count FROM order_items;

    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE 'Users: %', user_count;
    RAISE NOTICE 'Products: %', product_count;
    RAISE NOTICE 'Orders: %', order_count;
    RAISE NOTICE 'Order Items: %', order_item_count;
    RAISE NOTICE 'Total rows: %', user_count + product_count + order_count + order_item_count;
END $$;
