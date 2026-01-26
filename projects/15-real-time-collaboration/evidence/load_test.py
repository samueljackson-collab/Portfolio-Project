import asyncio
import csv
import json
import time
import uuid
from typing import List, Tuple

import websockets


async def connect_client(index: int, document_id: str):
    websocket = await websockets.connect("ws://localhost:8765")
    await websocket.send(
        json.dumps(
            {
                "document_id": document_id,
                "user_id": f"load-{index}-{uuid.uuid4().hex[:6]}",
                "username": f"LoadUser{index}",
            }
        )
    )
    return websocket


async def measure_ack_latency(websocket, operation_payload: dict) -> float:
    start = time.perf_counter()
    ack_event = asyncio.Event()

    async def receiver():
        async for message in websocket:
            payload = json.loads(message)
            if payload.get("type") == "ack":
                ack_event.set()
                break

    recv_task = asyncio.create_task(receiver())
    await websocket.send(json.dumps(operation_payload))
    await asyncio.wait_for(ack_event.wait(), timeout=10.0)
    latency = (time.perf_counter() - start) * 1000
    recv_task.cancel()
    await asyncio.gather(recv_task, return_exceptions=True)
    return latency


async def run_round(concurrency: int) -> Tuple[int, float]:
    document_id = f"load-doc-{concurrency}"
    clients = [await connect_client(i, document_id) for i in range(concurrency)]
    await asyncio.sleep(0.2)

    async def send_for_client(idx: int, websocket):
        payload = {
            "type": "operation",
            "operation": {
                "type": "insert",
                "position": 0,
                "content": f"user{idx} ",
                "length": 0,
                "version": 0,
            },
        }
        return await measure_ack_latency(websocket, payload)

    latencies = await asyncio.gather(
        *[send_for_client(idx, ws) for idx, ws in enumerate(clients)]
    )

    for ws in clients:
        await ws.close()

    avg_latency = sum(latencies) / len(latencies)
    return concurrency, avg_latency


async def main():
    concurrency_levels = [1, 2, 5, 10]
    results: List[Tuple[int, float]] = []

    for level in concurrency_levels:
        result = await run_round(level)
        results.append(result)
        await asyncio.sleep(0.2)

    with open(Path(__file__).parent / "load_test_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["concurrent_users", "avg_latency_ms"])
        writer.writerows(results)


if __name__ == "__main__":
    asyncio.run(main())
