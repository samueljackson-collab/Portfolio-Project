from fastapi import FastAPI
import os
import threading
import pika

from .telemetry import configure_tracing

configure_tracing("notification-service")

app = FastAPI(title="Notification Service")


def consume():
    queue_url = os.getenv("RABBITMQ_URL")
    if not queue_url:
        return

    connection = pika.BlockingConnection(pika.URLParameters(queue_url))
    channel = connection.channel()
    channel.queue_declare(queue="notifications", durable=True)

    def callback(ch, method, properties, body):
        print(f"Notification received: {body.decode('utf-8')}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="notifications", on_message_callback=callback)
    channel.start_consuming()


@app.on_event("startup")
async def start_consumer():
    thread = threading.Thread(target=consume, daemon=True)
    thread.start()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification-service"}
