import asyncio
import json
import time
import uuid
from typing import Dict

import websockets


async def connect_client(name: str, document_id: str, log: Dict[str, list]):
    uri = "ws://localhost:8765"
    user_id = f"{name.lower()}-{uuid.uuid4().hex[:6]}"
    websocket = await websockets.connect(uri)
    await websocket.send(
        json.dumps(
            {
                "document_id": document_id,
                "user_id": user_id,
                "username": name,
            }
        )
    )
    log[name].append(f"{name} authenticated as {user_id}")

    async def receiver():
        async for message in websocket:
            payload = json.loads(message)
            log[name].append(f"{name} received: {payload}")

    recv_task = asyncio.create_task(receiver())
    await asyncio.sleep(0.5)
    return websocket, recv_task


async def main():
    document_id = "demo-doc"
    log: Dict[str, list] = {"ClientA": [], "ClientB": []}

    client_a, recv_a = await connect_client("ClientA", document_id, log)
    client_b, recv_b = await connect_client("ClientB", document_id, log)

    await asyncio.sleep(0.5)

    operation_a = {
        "type": "operation",
        "operation": {
            "type": "insert",
            "position": 0,
            "content": "Hello from ClientA. ",
            "length": 0,
            "version": 0,
        },
    }
    await client_a.send(json.dumps(operation_a))
    log["ClientA"].append("ClientA sent insert operation")

    await asyncio.sleep(0.5)

    operation_b = {
        "type": "operation",
        "operation": {
            "type": "insert",
            "position": 22,
            "content": "ClientB syncs now.",
            "length": 0,
            "version": 0,
        },
    }
    await client_b.send(json.dumps(operation_b))
    log["ClientB"].append("ClientB sent insert operation")

    await asyncio.sleep(1.0)

    recv_a.cancel()
    recv_b.cancel()
    await asyncio.gather(recv_a, recv_b, return_exceptions=True)

    await client_a.close()
    await client_b.close()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Multi-client demo run at {timestamp}")
    for name, entries in log.items():
        print(f"\n--- {name} log ---")
        for entry in entries:
            print(entry)


if __name__ == "__main__":
    asyncio.run(main())
