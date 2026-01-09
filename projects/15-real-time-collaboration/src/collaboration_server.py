"""Minimal collaborative editing server using websockets and CRDT fallback."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Dict, List, Set

import websockets


@dataclass
class Operation:
    position: int
    insert: str


class DocumentSession:
    def __init__(self) -> None:
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.text: str = ""

    async def broadcast(self, message: Dict[str, str]) -> None:
        if not self.clients:
            return
        payload = json.dumps(message)
        await asyncio.gather(*[client.send(payload) for client in self.clients])


class CollaborationServer:
    def __init__(self) -> None:
        self.sessions: Dict[str, DocumentSession] = {}

    async def handler(
        self, websocket: websockets.WebSocketServerProtocol, path: str
    ) -> None:  # noqa: ARG002
        doc_id = websocket.request_headers.get("x-document-id", "default")
        session = self.sessions.setdefault(doc_id, DocumentSession())
        session.clients.add(websocket)
        await websocket.send(json.dumps({"type": "snapshot", "text": session.text}))
        try:
            async for message in websocket:
                data = json.loads(message)
                op = Operation(**data)
                session.text = (
                    session.text[: op.position]
                    + op.insert
                    + session.text[op.position :]
                )
                await session.broadcast(
                    {"type": "op", "position": op.position, "insert": op.insert}
                )
        finally:
            session.clients.discard(websocket)


async def main() -> None:
    server = CollaborationServer()
    async with websockets.serve(server.handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
