import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_data():
    from app.models import Product, User, Order, OrderItem, Booking

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            return

        # Products - 10 items across electronics, books, clothing
        products = [
            Product(
                name="Sony WH-1000XM5 Wireless Headphones",
                category="electronics",
                price=349.99,
                stock=42,
                description="Industry-leading noise canceling with Auto NC Optimizer, 30-hour battery life, Speak-to-Chat technology.",
                sku="PRD-001",
            ),
            Product(
                name="Apple iPad Air 5th Generation",
                category="electronics",
                price=749.00,
                stock=18,
                description="M1 chip, 10.9-inch Liquid Retina display, 5G capable, USB-C connector.",
                sku="PRD-002",
            ),
            Product(
                name="Logitech MX Master 3S Mouse",
                category="electronics",
                price=99.99,
                stock=75,
                description="8K DPI sensor, quiet clicks, MagSpeed electromagnetic scrolling, works on any surface.",
                sku="PRD-003",
            ),
            Product(
                name="Samsung 27-inch 4K Monitor",
                category="electronics",
                price=429.95,
                stock=23,
                description="UHD 4K resolution, 60Hz refresh rate, HDR10, USB-C connectivity, adjustable stand.",
                sku="PRD-004",
            ),
            Product(
                name="Clean Code by Robert C. Martin",
                category="books",
                price=38.99,
                stock=120,
                description="A handbook of agile software craftsmanship. Essential reading for every software developer.",
                sku="PRD-005",
            ),
            Product(
                name="Designing Data-Intensive Applications",
                category="books",
                price=54.99,
                stock=85,
                description="By Martin Kleppmann. The big ideas behind reliable, scalable, and maintainable systems.",
                sku="PRD-006",
            ),
            Product(
                name="The Pragmatic Programmer 20th Anniversary",
                category="books",
                price=49.99,
                stock=67,
                description="By David Thomas and Andrew Hunt. Your journey to mastery, updated for modern development.",
                sku="PRD-007",
            ),
            Product(
                name="Patagonia Better Sweater Fleece Jacket",
                category="clothing",
                price=139.00,
                stock=34,
                description="Classic fleece jacket made from 100% recycled polyester. Fair Trade Certified sewn.",
                sku="PRD-008",
            ),
            Product(
                name="Levi's 511 Slim Fit Jeans",
                category="clothing",
                price=69.50,
                stock=98,
                description="Slim fit through the thigh and leg opening. Sits below the waist. Stretch denim.",
                sku="PRD-009",
            ),
            Product(
                name="Allbirds Men's Tree Runners",
                category="clothing",
                price=118.00,
                stock=56,
                description="Made with FSC-certified eucalyptus tree fiber. Lightweight, breathable, machine washable.",
                sku="PRD-010",
            ),
        ]
        db.add_all(products)
        db.flush()

        # Users - 5 real-looking users
        users = [
            User(
                name="Alexandra Chen",
                email="alex.chen@gmail.com",
                created_at=datetime(2024, 1, 15, 9, 30, 0),
            ),
            User(
                name="Marcus Johnson",
                email="marcus.j@outlook.com",
                created_at=datetime(2024, 2, 3, 14, 22, 0),
            ),
            User(
                name="Priya Patel",
                email="priya.patel@yahoo.com",
                created_at=datetime(2024, 2, 28, 11, 5, 0),
            ),
            User(
                name="David Kowalski",
                email="d.kowalski@company.com",
                created_at=datetime(2024, 3, 10, 16, 45, 0),
            ),
            User(
                name="Sofia Martinez",
                email="sofia.martinez@proton.me",
                created_at=datetime(2024, 3, 22, 8, 15, 0),
            ),
        ]
        db.add_all(users)
        db.flush()

        # Orders - 5 orders with items
        order1 = Order(
            user_id=users[0].id,
            status="delivered",
            total=449.98,
            created_at=datetime(2024, 3, 5, 10, 0, 0),
        )
        db.add(order1)
        db.flush()
        db.add_all([
            OrderItem(order_id=order1.id, product_id=products[0].id, quantity=1, unit_price=349.99),
            OrderItem(order_id=order1.id, product_id=products[4].id, quantity=1, unit_price=38.99),
            OrderItem(order_id=order1.id, product_id=products[8].id, quantity=1, unit_price=69.50),
        ])

        order2 = Order(
            user_id=users[1].id,
            status="shipped",
            total=179.49,
            created_at=datetime(2024, 3, 12, 15, 30, 0),
        )
        db.add(order2)
        db.flush()
        db.add_all([
            OrderItem(order_id=order2.id, product_id=products[1].id, quantity=1, unit_price=749.00),
            OrderItem(order_id=order2.id, product_id=products[2].id, quantity=1, unit_price=99.99),
        ])

        order3 = Order(
            user_id=users[2].id,
            status="processing",
            total=593.93,
            created_at=datetime(2024, 3, 18, 9, 45, 0),
        )
        db.add(order3)
        db.flush()
        db.add_all([
            OrderItem(order_id=order3.id, product_id=products[5].id, quantity=2, unit_price=54.99),
            OrderItem(order_id=order3.id, product_id=products[6].id, quantity=1, unit_price=49.99),
            OrderItem(order_id=order3.id, product_id=products[3].id, quantity=1, unit_price=429.95),
        ])

        order4 = Order(
            user_id=users[3].id,
            status="pending",
            total=257.00,
            created_at=datetime(2024, 3, 20, 11, 0, 0),
        )
        db.add(order4)
        db.flush()
        db.add_all([
            OrderItem(order_id=order4.id, product_id=products[7].id, quantity=1, unit_price=139.00),
            OrderItem(order_id=order4.id, product_id=products[9].id, quantity=1, unit_price=118.00),
        ])

        order5 = Order(
            user_id=users[4].id,
            status="delivered",
            total=649.95,
            created_at=datetime(2024, 3, 25, 14, 0, 0),
        )
        db.add(order5)
        db.flush()
        db.add_all([
            OrderItem(order_id=order5.id, product_id=products[1].id, quantity=1, unit_price=749.00),
            OrderItem(order_id=order5.id, product_id=products[4].id, quantity=1, unit_price=38.99),
            OrderItem(order_id=order5.id, product_id=products[8].id, quantity=1, unit_price=69.50),
        ])

        # Bookings - 5 slots (conference rooms and appointment types)
        bookings = [
            Booking(
                user_id=users[0].id,
                resource_name="Conference Room Alpha",
                start_time=datetime(2026, 3, 20, 9, 0, 0),
                end_time=datetime(2026, 3, 20, 10, 30, 0),
                status="confirmed",
                notes="Q1 Planning Meeting - Engineering team sync",
            ),
            Booking(
                user_id=users[1].id,
                resource_name="Conference Room Beta",
                start_time=datetime(2026, 3, 20, 13, 0, 0),
                end_time=datetime(2026, 3, 20, 14, 0, 0),
                status="confirmed",
                notes="Client demo for Acme Corp product walkthrough",
            ),
            Booking(
                user_id=users[2].id,
                resource_name="Medical Consultation Suite",
                start_time=datetime(2026, 3, 21, 10, 0, 0),
                end_time=datetime(2026, 3, 21, 10, 45, 0),
                status="confirmed",
                notes="Annual health checkup appointment",
            ),
            Booking(
                user_id=users[3].id,
                resource_name="Conference Room Alpha",
                start_time=datetime(2026, 3, 21, 14, 0, 0),
                end_time=datetime(2026, 3, 21, 16, 0, 0),
                status="confirmed",
                notes="Budget review and headcount planning session",
            ),
            Booking(
                user_id=users[4].id,
                resource_name="Training Room Gamma",
                start_time=datetime(2026, 3, 22, 9, 0, 0),
                end_time=datetime(2026, 3, 22, 12, 0, 0),
                status="confirmed",
                notes="New employee onboarding workshop - cohort March 2026",
            ),
        ]
        db.add_all(bookings)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
