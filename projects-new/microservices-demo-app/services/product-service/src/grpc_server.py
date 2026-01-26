import grpc
from concurrent import futures
import json

PRODUCTS = {
    "sku-1": {"product_id": "sku-1", "name": "Demo Laptop", "price": 1299.0},
    "sku-2": {"product_id": "sku-2", "name": "Wireless Mouse", "price": 49.0},
}


def request_deserializer(message: bytes):
    payload = json.loads(message.decode("utf-8"))
    return payload.get("product_id")


def response_serializer(message: dict):
    return json.dumps(message).encode("utf-8")


def get_product_handler(product_id: str):
    return PRODUCTS.get(
        product_id,
        {
            "product_id": product_id,
            "name": "Unknown",
            "price": 0.0,
        },
    )


def serve() -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    method_handler = grpc.unary_unary_rpc_method_handler(
        get_product_handler,
        request_deserializer=request_deserializer,
        response_serializer=response_serializer,
    )
    service = grpc.method_handlers_generic_handler(
        "product.ProductCatalog",
        {"GetProduct": method_handler},
    )
    server.add_generic_rpc_handlers((service,))
    server.add_insecure_port("[::]:50051")
    server.start()
    return server
