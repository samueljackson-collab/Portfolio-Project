from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import pika

from .telemetry import configure_tracing
from .grpc_client import fetch_product

configure_tracing("order-service")

app = FastAPI(title="Order Service")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "order-service"}


@app.post("/orders")
async def create_order(payload: dict):
    product_id = payload.get("product_id")
    if not product_id:
        return JSONResponse(status_code=400, content={"error": "missing_product"})

    product = fetch_product(
        os.getenv("PRODUCT_GRPC_HOST", "localhost"),
        int(os.getenv("PRODUCT_GRPC_PORT", "50051")),
        product_id,
    )

    message = {
        "order_id": "order-123",
        "product": product,
        "status": "created",
    }

    queue_url = os.getenv("RABBITMQ_URL")
    if queue_url:
        connection = pika.BlockingConnection(pika.URLParameters(queue_url))
        channel = connection.channel()
        channel.queue_declare(queue="notifications", durable=True)
        channel.basic_publish(
            exchange="",
            routing_key="notifications",
            body=str(message).encode("utf-8"),
        )
        connection.close()

    return message
