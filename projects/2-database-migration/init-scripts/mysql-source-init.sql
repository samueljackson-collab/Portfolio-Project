-- MySQL Source Database Initialization
-- Demonstrates common MySQL data types including ENUMs for migration testing

-- Grant replication privileges to debezium user
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
GRANT SELECT, RELOAD, SHOW DATABASES, LOCK TABLES ON *.* TO 'debezium'@'%';
FLUSH PRIVILEGES;

-- Create users table with MySQL-specific features
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    status ENUM('active', 'inactive', 'suspended', 'deleted') DEFAULT 'active',
    role ENUM('admin', 'manager', 'user', 'guest') DEFAULT 'user',
    profile_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category ENUM('electronics', 'clothing', 'food', 'books', 'toys', 'other') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock_quantity INT UNSIGNED DEFAULT 0,
    weight_kg DECIMAL(8, 3),
    is_active TINYINT(1) DEFAULT 1,
    attributes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_sku (sku)
) ENGINE=InnoDB;

-- Create orders table (large dataset simulation)
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
    payment_status ENUM('unpaid', 'paid', 'refunded', 'failed') DEFAULT 'unpaid',
    payment_method ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash') DEFAULT 'credit_card',
    subtotal DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0.00,
    shipping_amount DECIMAL(10, 2) DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    shipping_address JSON,
    billing_address JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_payment_status (payment_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id INT NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    line_total DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB;

-- Create inventory_log table for CDC testing
CREATE TABLE IF NOT EXISTS inventory_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_type ENUM('purchase', 'sale', 'adjustment', 'return', 'damaged') NOT NULL,
    quantity_change INT NOT NULL,
    previous_quantity INT NOT NULL,
    new_quantity INT NOT NULL,
    reference_id BIGINT,
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_product_id (product_id),
    INDEX idx_change_type (change_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- Insert sample users
INSERT INTO users (username, email, status, role, profile_data) VALUES
    ('admin', 'admin@example.com', 'active', 'admin', '{"department": "IT", "phone": "+1-555-0100"}'),
    ('alice_johnson', 'alice@example.com', 'active', 'manager', '{"department": "Sales", "phone": "+1-555-0101"}'),
    ('bob_smith', 'bob@example.com', 'active', 'user', '{"department": "Marketing", "phone": "+1-555-0102"}'),
    ('charlie_brown', 'charlie@example.com', 'active', 'user', '{"department": "Engineering", "phone": "+1-555-0103"}'),
    ('diana_ross', 'diana@example.com', 'inactive', 'user', '{"department": "HR", "phone": "+1-555-0104"}'),
    ('edward_jones', 'edward@example.com', 'active', 'manager', '{"department": "Finance", "phone": "+1-555-0105"}'),
    ('fiona_green', 'fiona@example.com', 'active', 'user', '{"department": "Sales", "phone": "+1-555-0106"}'),
    ('george_white', 'george@example.com', 'suspended', 'user', '{"department": "Support", "phone": "+1-555-0107"}'),
    ('hannah_black', 'hannah@example.com', 'active', 'user', '{"department": "Engineering", "phone": "+1-555-0108"}'),
    ('ivan_gray', 'ivan@example.com', 'active', 'guest', '{"department": "External", "phone": "+1-555-0109"}');

-- Insert sample products
INSERT INTO products (sku, name, description, category, price, cost, stock_quantity, weight_kg, attributes) VALUES
    ('ELEC-001', 'MacBook Pro 16"', 'Apple MacBook Pro with M3 chip', 'electronics', 2499.99, 2000.00, 50, 2.140, '{"brand": "Apple", "color": "Space Gray", "warranty_months": 12}'),
    ('ELEC-002', 'iPhone 15 Pro', 'Apple iPhone 15 Pro 256GB', 'electronics', 1199.99, 800.00, 200, 0.187, '{"brand": "Apple", "color": "Natural Titanium", "storage": "256GB"}'),
    ('ELEC-003', 'Samsung 4K TV 55"', 'Samsung QLED 4K Smart TV', 'electronics', 899.99, 600.00, 75, 18.500, '{"brand": "Samsung", "screen_size": "55 inch", "resolution": "4K"}'),
    ('ELEC-004', 'Sony WH-1000XM5', 'Wireless Noise Cancelling Headphones', 'electronics', 349.99, 200.00, 150, 0.250, '{"brand": "Sony", "color": "Black", "battery_hours": 30}'),
    ('CLTH-001', 'Nike Air Max 90', 'Classic Nike sneakers', 'clothing', 129.99, 60.00, 300, 0.850, '{"brand": "Nike", "sizes": ["7", "8", "9", "10", "11", "12"]}'),
    ('CLTH-002', 'Levi''s 501 Jeans', 'Original fit jeans', 'clothing', 89.99, 35.00, 500, 0.650, '{"brand": "Levis", "material": "100% Cotton"}'),
    ('BOOK-001', 'Clean Code', 'A Handbook of Agile Software Craftsmanship', 'books', 44.99, 20.00, 100, 0.680, '{"author": "Robert C. Martin", "pages": 464, "isbn": "978-0132350884"}'),
    ('BOOK-002', 'Design Patterns', 'Elements of Reusable Object-Oriented Software', 'books', 54.99, 25.00, 80, 0.750, '{"authors": ["Gang of Four"], "pages": 416}'),
    ('FOOD-001', 'Organic Coffee Beans', '1kg Premium Arabica beans', 'food', 24.99, 12.00, 400, 1.000, '{"origin": "Colombia", "roast": "Medium"}'),
    ('TOYS-001', 'LEGO Star Wars Set', 'Millennium Falcon 75257', 'toys', 169.99, 100.00, 60, 1.200, '{"pieces": 1351, "ages": "9+", "brand": "LEGO"}');

-- Generate large orders dataset (100 orders)
DELIMITER //
CREATE PROCEDURE generate_orders()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE user_id INT;
    DECLARE order_num VARCHAR(50);
    DECLARE subtotal DECIMAL(12,2);
    DECLARE tax DECIMAL(10,2);
    DECLARE shipping DECIMAL(10,2);
    DECLARE discount DECIMAL(10,2);
    DECLARE total DECIMAL(12,2);
    DECLARE order_status VARCHAR(20);
    DECLARE payment_stat VARCHAR(20);
    DECLARE payment_meth VARCHAR(20);

    WHILE i <= 100 DO
        SET user_id = FLOOR(1 + RAND() * 10);
        SET order_num = CONCAT('ORD-', LPAD(i, 6, '0'));
        SET subtotal = ROUND(50 + RAND() * 2000, 2);
        SET tax = ROUND(subtotal * 0.08, 2);
        SET shipping = ROUND(5 + RAND() * 20, 2);
        SET discount = IF(RAND() > 0.7, ROUND(subtotal * 0.1, 2), 0);
        SET total = subtotal + tax + shipping - discount;

        SET order_status = ELT(FLOOR(1 + RAND() * 7), 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded');
        SET payment_stat = ELT(FLOOR(1 + RAND() * 4), 'unpaid', 'paid', 'refunded', 'failed');
        SET payment_meth = ELT(FLOOR(1 + RAND() * 5), 'credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash');

        INSERT INTO orders (user_id, order_number, status, payment_status, payment_method,
                           subtotal, tax_amount, shipping_amount, discount_amount, total_amount,
                           shipping_address, billing_address, created_at)
        VALUES (
            user_id, order_num, order_status, payment_stat, payment_meth,
            subtotal, tax, shipping, discount, total,
            JSON_OBJECT('street', CONCAT(FLOOR(100 + RAND() * 9900), ' Main St'), 'city', 'New York', 'state', 'NY', 'zip', '10001'),
            JSON_OBJECT('street', CONCAT(FLOOR(100 + RAND() * 9900), ' Oak Ave'), 'city', 'New York', 'state', 'NY', 'zip', '10001'),
            DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 365) DAY)
        );

        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL generate_orders();
DROP PROCEDURE generate_orders;

-- Generate order items for each order
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_percent, line_total)
SELECT
    o.id,
    p.id,
    FLOOR(1 + RAND() * 3),
    p.price,
    IF(RAND() > 0.8, ROUND(RAND() * 15, 2), 0),
    ROUND(p.price * FLOOR(1 + RAND() * 3) * (1 - IF(RAND() > 0.8, RAND() * 0.15, 0)), 2)
FROM orders o
CROSS JOIN products p
WHERE RAND() < 0.3
LIMIT 300;

-- Create trigger for inventory tracking
DELIMITER //
CREATE TRIGGER after_order_item_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    DECLARE current_qty INT;
    SELECT stock_quantity INTO current_qty FROM products WHERE id = NEW.product_id;

    INSERT INTO inventory_log (product_id, change_type, quantity_change, previous_quantity, new_quantity, reference_id, notes)
    VALUES (NEW.product_id, 'sale', -NEW.quantity, current_qty, current_qty - NEW.quantity, NEW.order_id, CONCAT('Order item ', NEW.id));

    UPDATE products SET stock_quantity = stock_quantity - NEW.quantity WHERE id = NEW.product_id;
END //
DELIMITER ;

-- Display summary
SELECT 'MySQL Source Database Initialized' AS status;
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS product_count FROM products;
SELECT COUNT(*) AS order_count FROM orders;
SELECT COUNT(*) AS order_item_count FROM order_items;
