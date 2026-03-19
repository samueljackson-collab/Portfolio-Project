"""
Full test suite for the E-commerce & Booking Systems API.
Uses an in-memory SQLite database for isolation between test runs.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, seed_data as original_seed
from app.models import Product, User, Order, OrderItem, Booking
from app.main import app

# ─── Test Database Setup ──────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_ecommerce.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_test_data():
    """Seed the test database with the same data as production."""
    from datetime import datetime

    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        if db.query(Product).count() > 0:
            return

        products = [
            Product(name="Sony WH-1000XM5 Wireless Headphones", category="electronics", price=349.99, stock=42, description="Industry-leading noise canceling with Auto NC Optimizer, 30-hour battery life.", sku="PRD-001"),
            Product(name="Apple iPad Air 5th Generation", category="electronics", price=749.00, stock=18, description="M1 chip, 10.9-inch Liquid Retina display, 5G capable, USB-C connector.", sku="PRD-002"),
            Product(name="Logitech MX Master 3S Mouse", category="electronics", price=99.99, stock=75, description="8K DPI sensor, quiet clicks, MagSpeed electromagnetic scrolling.", sku="PRD-003"),
            Product(name="Samsung 27-inch 4K Monitor", category="electronics", price=429.95, stock=23, description="UHD 4K resolution, 60Hz refresh rate, HDR10, USB-C connectivity.", sku="PRD-004"),
            Product(name="Clean Code by Robert C. Martin", category="books", price=38.99, stock=120, description="A handbook of agile software craftsmanship.", sku="PRD-005"),
            Product(name="Designing Data-Intensive Applications", category="books", price=54.99, stock=85, description="By Martin Kleppmann. Reliable, scalable, maintainable systems.", sku="PRD-006"),
            Product(name="The Pragmatic Programmer 20th Anniversary", category="books", price=49.99, stock=67, description="By David Thomas and Andrew Hunt.", sku="PRD-007"),
            Product(name="Patagonia Better Sweater Fleece Jacket", category="clothing", price=139.00, stock=34, description="Made from 100% recycled polyester. Fair Trade Certified.", sku="PRD-008"),
            Product(name="Levi's 511 Slim Fit Jeans", category="clothing", price=69.50, stock=98, description="Slim fit through the thigh and leg opening. Stretch denim.", sku="PRD-009"),
            Product(name="Allbirds Men's Tree Runners", category="clothing", price=118.00, stock=56, description="FSC-certified eucalyptus tree fiber. Lightweight, breathable.", sku="PRD-010"),
        ]
        db.add_all(products)
        db.flush()

        users = [
            User(name="Alexandra Chen", email="alex.chen@gmail.com", created_at=datetime(2024, 1, 15, 9, 30, 0)),
            User(name="Marcus Johnson", email="marcus.j@outlook.com", created_at=datetime(2024, 2, 3, 14, 22, 0)),
            User(name="Priya Patel", email="priya.patel@yahoo.com", created_at=datetime(2024, 2, 28, 11, 5, 0)),
            User(name="David Kowalski", email="d.kowalski@company.com", created_at=datetime(2024, 3, 10, 16, 45, 0)),
            User(name="Sofia Martinez", email="sofia.martinez@proton.me", created_at=datetime(2024, 3, 22, 8, 15, 0)),
        ]
        db.add_all(users)
        db.flush()

        order1 = Order(user_id=users[0].id, status="delivered", total=449.98, created_at=datetime(2024, 3, 5, 10, 0, 0))
        db.add(order1)
        db.flush()
        db.add_all([
            OrderItem(order_id=order1.id, product_id=products[0].id, quantity=1, unit_price=349.99),
            OrderItem(order_id=order1.id, product_id=products[4].id, quantity=1, unit_price=38.99),
            OrderItem(order_id=order1.id, product_id=products[8].id, quantity=1, unit_price=69.50),
        ])

        order2 = Order(user_id=users[1].id, status="shipped", total=179.49, created_at=datetime(2024, 3, 12, 15, 30, 0))
        db.add(order2)
        db.flush()
        db.add_all([
            OrderItem(order_id=order2.id, product_id=products[1].id, quantity=1, unit_price=749.00),
            OrderItem(order_id=order2.id, product_id=products[2].id, quantity=1, unit_price=99.99),
        ])

        order3 = Order(user_id=users[2].id, status="processing", total=593.93, created_at=datetime(2024, 3, 18, 9, 45, 0))
        db.add(order3)
        db.flush()
        db.add_all([
            OrderItem(order_id=order3.id, product_id=products[5].id, quantity=2, unit_price=54.99),
            OrderItem(order_id=order3.id, product_id=products[6].id, quantity=1, unit_price=49.99),
            OrderItem(order_id=order3.id, product_id=products[3].id, quantity=1, unit_price=429.95),
        ])

        order4 = Order(user_id=users[3].id, status="pending", total=257.00, created_at=datetime(2024, 3, 20, 11, 0, 0))
        db.add(order4)
        db.flush()
        db.add_all([
            OrderItem(order_id=order4.id, product_id=products[7].id, quantity=1, unit_price=139.00),
            OrderItem(order_id=order4.id, product_id=products[9].id, quantity=1, unit_price=118.00),
        ])

        order5 = Order(user_id=users[4].id, status="delivered", total=649.95, created_at=datetime(2024, 3, 25, 14, 0, 0))
        db.add(order5)
        db.flush()
        db.add_all([
            OrderItem(order_id=order5.id, product_id=products[1].id, quantity=1, unit_price=749.00),
            OrderItem(order_id=order5.id, product_id=products[4].id, quantity=1, unit_price=38.99),
            OrderItem(order_id=order5.id, product_id=products[8].id, quantity=1, unit_price=69.50),
        ])

        bookings = [
            Booking(user_id=users[0].id, resource_name="Conference Room Alpha", start_time=datetime(2026, 3, 20, 9, 0, 0), end_time=datetime(2026, 3, 20, 10, 30, 0), status="confirmed", notes="Q1 Planning Meeting"),
            Booking(user_id=users[1].id, resource_name="Conference Room Beta", start_time=datetime(2026, 3, 20, 13, 0, 0), end_time=datetime(2026, 3, 20, 14, 0, 0), status="confirmed", notes="Client demo"),
            Booking(user_id=users[2].id, resource_name="Medical Consultation Suite", start_time=datetime(2026, 3, 21, 10, 0, 0), end_time=datetime(2026, 3, 21, 10, 45, 0), status="confirmed", notes="Annual checkup"),
            Booking(user_id=users[3].id, resource_name="Conference Room Alpha", start_time=datetime(2026, 3, 21, 14, 0, 0), end_time=datetime(2026, 3, 21, 16, 0, 0), status="confirmed", notes="Budget review"),
            Booking(user_id=users[4].id, resource_name="Training Room Gamma", start_time=datetime(2026, 3, 22, 9, 0, 0), end_time=datetime(2026, 3, 22, 12, 0, 0), status="confirmed", notes="Onboarding workshop"),
        ]
        db.add_all(bookings)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables and seed data once for the entire test session."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    seed_test_data()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def client(setup_test_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["version"] == "1.0.0"


def test_list_products(client):
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 10
    skus = [p["sku"] for p in products]
    assert "PRD-001" in skus
    assert "PRD-010" in skus


def test_filter_products_by_category(client):
    response = client.get("/products?category=electronics")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 4
    for p in products:
        assert p["category"] == "electronics"

    response = client.get("/products?category=books")
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get("/products?category=clothing")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_filter_products_by_price(client):
    response = client.get("/products?max_price=100")
    assert response.status_code == 200
    products = response.json()
    for p in products:
        assert p["price"] <= 100

    response = client.get("/products?min_price=100&max_price=200")
    assert response.status_code == 200
    products = response.json()
    for p in products:
        assert 100 <= p["price"] <= 200


def test_get_product_by_id(client):
    response = client.get("/products/1")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == 1
    assert product["sku"] == "PRD-001"
    assert product["name"] == "Sony WH-1000XM5 Wireless Headphones"
    assert product["category"] == "electronics"
    assert product["price"] == 349.99


def test_get_product_not_found(client):
    response = client.get("/products/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_product(client):
    payload = {
        "name": "Mechanical Keyboard Keychron K2",
        "category": "electronics",
        "price": 89.99,
        "stock": 30,
        "description": "Wireless mechanical keyboard with hot-swappable switches.",
        "sku": "PRD-NEW-001",
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    product = response.json()
    assert product["id"] is not None
    assert product["name"] == "Mechanical Keyboard Keychron K2"
    assert product["sku"] == "PRD-NEW-001"
    assert product["price"] == 89.99
    assert product["stock"] == 30


def test_create_product_duplicate_sku(client):
    payload = {
        "name": "Duplicate SKU Product",
        "category": "electronics",
        "price": 49.99,
        "stock": 10,
        "sku": "PRD-001",  # Already exists
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 409


def test_list_orders(client):
    response = client.get("/orders")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 5
    statuses = {o["status"] for o in orders}
    assert "delivered" in statuses
    assert "pending" in statuses


def test_get_order_by_id(client):
    response = client.get("/orders/1")
    assert response.status_code == 200
    order = response.json()
    assert order["id"] == 1
    assert order["user_id"] == 1
    assert order["status"] == "delivered"
    assert len(order["items"]) > 0


def test_create_order(client):
    payload = {
        "user_id": 1,
        "items": [
            {"product_id": 3, "quantity": 2},
            {"product_id": 5, "quantity": 1},
        ],
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    order = response.json()
    assert order["id"] is not None
    assert order["user_id"] == 1
    assert order["status"] == "pending"
    assert len(order["items"]) == 2
    # 2 x 99.99 + 1 x 38.99
    assert abs(order["total"] - 238.97) < 0.01


def test_create_order_invalid_user(client):
    payload = {
        "user_id": 9999,
        "items": [{"product_id": 1, "quantity": 1}],
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 404


def test_list_bookings(client):
    response = client.get("/bookings")
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) == 5
    resources = [b["resource_name"] for b in bookings]
    assert "Conference Room Alpha" in resources
    assert "Training Room Gamma" in resources


def test_filter_bookings_by_resource(client):
    response = client.get("/bookings?resource=Conference Room Alpha")
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) == 2
    for b in bookings:
        assert b["resource_name"] == "Conference Room Alpha"


def test_get_booking(client):
    response = client.get("/bookings/1")
    assert response.status_code == 200
    booking = response.json()
    assert booking["id"] == 1
    assert booking["resource_name"] == "Conference Room Alpha"
    assert booking["status"] == "confirmed"
    assert booking["user_id"] == 1


def test_create_booking(client):
    payload = {
        "user_id": 2,
        "resource_name": "Conference Room Delta",
        "start_time": "2026-04-01T09:00:00",
        "end_time": "2026-04-01T10:00:00",
        "notes": "Weekly team standup",
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 201
    booking = response.json()
    assert booking["id"] is not None
    assert booking["resource_name"] == "Conference Room Delta"
    assert booking["status"] == "confirmed"
    assert booking["notes"] == "Weekly team standup"


def test_booking_overlap_rejected(client):
    # First booking on a new resource
    payload1 = {
        "user_id": 1,
        "resource_name": "Boardroom Suite",
        "start_time": "2026-05-01T10:00:00",
        "end_time": "2026-05-01T12:00:00",
        "notes": "Strategy session",
    }
    response1 = client.post("/bookings", json=payload1)
    assert response1.status_code == 201

    # Overlapping booking on the same resource (starts during first booking)
    payload2 = {
        "user_id": 2,
        "resource_name": "Boardroom Suite",
        "start_time": "2026-05-01T11:00:00",  # overlaps with 10:00-12:00
        "end_time": "2026-05-01T13:00:00",
        "notes": "Another meeting",
    }
    response2 = client.post("/bookings", json=payload2)
    assert response2.status_code == 409
    assert "conflict" in response2.json()["detail"].lower()


def test_delete_booking(client):
    # Create a booking to delete
    payload = {
        "user_id": 3,
        "resource_name": "Quiet Focus Room",
        "start_time": "2026-06-01T14:00:00",
        "end_time": "2026-06-01T15:00:00",
        "notes": "Deep work session",
    }
    create_resp = client.post("/bookings", json=payload)
    assert create_resp.status_code == 201
    booking_id = create_resp.json()["id"]

    # Delete (cancel) the booking
    delete_resp = client.delete(f"/bookings/{booking_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["id"] == booking_id

    # Verify it's cancelled (still retrievable but status is cancelled)
    get_resp = client.get(f"/bookings/{booking_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "cancelled"
