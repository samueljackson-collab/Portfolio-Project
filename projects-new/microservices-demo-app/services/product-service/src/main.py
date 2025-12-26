from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading

from .telemetry import configure_tracing
from .grpc_server import serve, PRODUCTS

configure_tracing("product-service")

app = FastAPI(title="Product Service")


@app.on_event("startup")
async def start_grpc():
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "product-service"}


@app.get("/products")
async def list_products():
    return {"items": list(PRODUCTS.values())}


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    product = PRODUCTS.get(product_id)
    if not product:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    return product
