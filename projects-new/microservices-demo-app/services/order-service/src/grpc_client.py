import grpc
import json


def fetch_product(host: str, port: int, product_id: str):
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = channel.unary_unary(
        "/product.ProductCatalog/GetProduct",
        request_serializer=lambda payload: json.dumps(payload).encode("utf-8"),
        response_deserializer=lambda payload: json.loads(payload.decode("utf-8")),
    )
    response = stub({"product_id": product_id})
    return response
