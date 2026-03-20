from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime

from app.database import get_db, seed_data
from app.models import Product, User, Order, OrderItem, Booking
from app.schemas import (
    ProductCreate, ProductResponse,
    OrderCreate, OrderResponse,
    BookingCreate, BookingResponse,
    HealthResponse,
)

app = FastAPI(
    title="E-commerce & Booking Systems API",
    description="A production-ready REST API for managing products, orders, and resource bookings.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def startup_event():
    seed_data()


# ─── Root & Health ────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {
        "name": "E-commerce & Booking Systems API",
        "version": "1.0.0",
        "description": "REST API for products, orders, and resource bookings",
        "endpoints": {
            "products": "/products",
            "orders": "/orders",
            "bookings": "/bookings",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok", database=db_status, version="1.0.0")


# ─── Products ─────────────────────────────────────────────────────────────────

@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    return query.offset(skip).limit(limit).all()


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@app.post("/products", response_model=ProductResponse, status_code=201, tags=["Products"])
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"SKU '{payload.sku}' already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ─── Orders ───────────────────────────────────────────────────────────────────

@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return db.query(Order).offset(skip).limit(limit).all()


@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

    if not payload.items:
        raise HTTPException(status_code=422, detail="Order must have at least one item")

    order = Order(user_id=payload.user_id, status="pending", total=0.0)
    db.add(order)
    db.flush()

    total = 0.0
    for item_data in payload.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Product {item_data.product_id} not found",
            )
        if product.stock < item_data.quantity:
            db.rollback()
            raise HTTPException(
                status_code=422,
                detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}, requested: {item_data.quantity}",
            )
        line_total = product.price * item_data.quantity
        total += line_total
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=product.price,
        ))
        product.stock -= item_data.quantity

    order.total = round(total, 2)
    db.commit()
    db.refresh(order)
    return order


# ─── Bookings ─────────────────────────────────────────────────────────────────

@app.get("/bookings", response_model=List[BookingResponse], tags=["Bookings"])
def list_bookings(
    resource: Optional[str] = Query(None, description="Filter by resource name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Booking)
    if resource:
        query = query.filter(Booking.resource_name == resource)
    return query.offset(skip).limit(limit).all()


@app.get("/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return booking


@app.post("/bookings", response_model=BookingResponse, status_code=201, tags=["Bookings"])
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

    # Check for overlapping bookings on the same resource
    overlap = db.query(Booking).filter(
        and_(
            Booking.resource_name == payload.resource_name,
            Booking.status != "cancelled",
            Booking.start_time < payload.end_time,
            Booking.end_time > payload.start_time,
        )
    ).first()

    if overlap:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Booking conflict: '{payload.resource_name}' is already reserved "
                f"from {overlap.start_time.isoformat()} to {overlap.end_time.isoformat()}"
            ),
        )

    booking = Booking(
        user_id=payload.user_id,
        resource_name=payload.resource_name,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status="confirmed",
        notes=payload.notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@app.delete("/bookings/{booking_id}", tags=["Bookings"])
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    booking.status = "cancelled"
    db.commit()
    return {"message": f"Booking {booking_id} has been cancelled", "id": booking_id}
