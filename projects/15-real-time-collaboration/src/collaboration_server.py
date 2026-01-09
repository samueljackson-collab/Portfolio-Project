"""Minimal collaborative editing server using websockets and CRDT fallback."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import hashlib

import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('collaboration-server')


class OperationType(Enum):
    """Types of operations."""
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"


@dataclass
class Operation:
    """An atomic editing operation."""
    op_type: OperationType
    position: int
    content: str = ""
    length: int = 0
    version: int = 0
    user_id: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.op_type.value,
            "position": self.position,
            "content": self.content,
            "length": self.length,
            "version": self.version,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Operation":
        return cls(
            op_type=OperationType(data["type"]),
            position=data["position"],
            content=data.get("content", ""),
            length=data.get("length", 0),
            version=data.get("version", 0),
            user_id=data.get("user_id", ""),
            timestamp=data.get("timestamp", time.time())
        )


@dataclass
class UserPresence:
    """User presence information."""
    user_id: str
    username: str
    color: str
    cursor_position: int = 0
    selection_start: int = 0
    selection_end: int = 0
    last_active: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "color": self.color,
            "cursor_position": self.cursor_position,
            "selection_start": self.selection_start,
            "selection_end": self.selection_end,
            "last_active": self.last_active
        }


class OperationalTransform:
    """
    Operational Transformation engine for conflict resolution.

    Implements the inclusion transformation (IT) algorithm for
    concurrent insert and delete operations.
    """

    @staticmethod
    def transform(op1: Operation, op2: Operation) -> Operation:
        """
        Transform op1 against op2.

        Args:
            op1: The operation to transform
            op2: The operation to transform against

        Returns:
            Transformed operation
        """
        if op1.op_type == OperationType.INSERT and op2.op_type == OperationType.INSERT:
            return OperationalTransform._transform_insert_insert(op1, op2)
        elif op1.op_type == OperationType.INSERT and op2.op_type == OperationType.DELETE:
            return OperationalTransform._transform_insert_delete(op1, op2)
        elif op1.op_type == OperationType.DELETE and op2.op_type == OperationType.INSERT:
            return OperationalTransform._transform_delete_insert(op1, op2)
        elif op1.op_type == OperationType.DELETE and op2.op_type == OperationType.DELETE:
            return OperationalTransform._transform_delete_delete(op1, op2)
        return op1

    @staticmethod
    def _transform_insert_insert(op1: Operation, op2: Operation) -> Operation:
        """Transform insert against insert."""
        if op1.position <= op2.position:
            return op1
        return Operation(
            op_type=OperationType.INSERT,
            position=op1.position + len(op2.content),
            content=op1.content,
            version=op1.version,
            user_id=op1.user_id
        )

    @staticmethod
    def _transform_insert_delete(op1: Operation, op2: Operation) -> Operation:
        """Transform insert against delete."""
        if op1.position <= op2.position:
            return op1
        elif op1.position >= op2.position + op2.length:
            return Operation(
                op_type=OperationType.INSERT,
                position=op1.position - op2.length,
                content=op1.content,
                version=op1.version,
                user_id=op1.user_id
            )
        else:
            return Operation(
                op_type=OperationType.INSERT,
                position=op2.position,
                content=op1.content,
                version=op1.version,
                user_id=op1.user_id
            )

    @staticmethod
    def _transform_delete_insert(op1: Operation, op2: Operation) -> Operation:
        """Transform delete against insert."""
        if op2.position >= op1.position + op1.length:
            return op1
        elif op2.position <= op1.position:
            return Operation(
                op_type=OperationType.DELETE,
                position=op1.position + len(op2.content),
                length=op1.length,
                version=op1.version,
                user_id=op1.user_id
            )
        else:
            # Insert is within delete range - split the delete
            return Operation(
                op_type=OperationType.DELETE,
                position=op1.position,
                length=op1.length + len(op2.content),
                version=op1.version,
                user_id=op1.user_id
            )

    @staticmethod
    def _transform_delete_delete(op1: Operation, op2: Operation) -> Operation:
        """Transform delete against delete."""
        if op1.position >= op2.position + op2.length:
            return Operation(
                op_type=OperationType.DELETE,
                position=op1.position - op2.length,
                length=op1.length,
                version=op1.version,
                user_id=op1.user_id
            )
        elif op1.position + op1.length <= op2.position:
            return op1
        else:
            # Overlapping deletes
            if op1.position >= op2.position:
                if op1.position + op1.length <= op2.position + op2.length:
                    # op1 is completely within op2
                    return Operation(
                        op_type=OperationType.RETAIN,
                        position=0,
                        length=0,
                        version=op1.version,
                        user_id=op1.user_id
                    )
                else:
                    return Operation(
                        op_type=OperationType.DELETE,
                        position=op2.position,
                        length=op1.position + op1.length - op2.position - op2.length,
                        version=op1.version,
                        user_id=op1.user_id
                    )
            else:
                if op1.position + op1.length <= op2.position + op2.length:
                    return Operation(
                        op_type=OperationType.DELETE,
                        position=op1.position,
                        length=op2.position - op1.position,
                        version=op1.version,
                        user_id=op1.user_id
                    )
                else:
                    return Operation(
                        op_type=OperationType.DELETE,
                        position=op1.position,
                        length=op1.length - op2.length,
                        version=op1.version,
                        user_id=op1.user_id
                    )


class DocumentSession:
    """
    Manages a collaborative editing session for a single document.

    Handles:
    - Client connections
    - Operation history and versioning
    - Conflict resolution via OT
    - User presence tracking
    """

    def __init__(self, document_id: str, initial_content: str = ""):
        self.document_id = document_id
        self.content = initial_content
        self.version = 0
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.presence: Dict[str, UserPresence] = {}
        self.operation_history: List[Operation] = []
        self.max_history_size = 1000
        self.ot = OperationalTransform()
        self._lock = asyncio.Lock()

    async def join(self, websocket: WebSocketServerProtocol, user: UserPresence):
        """Add a client to the session."""
        async with self._lock:
            self.clients[user.user_id] = websocket
            self.presence[user.user_id] = user

        # Send current document state
        await self._send_to_client(websocket, {
            "type": "snapshot",
            "document_id": self.document_id,
            "content": self.content,
            "version": self.version,
            "users": [p.to_dict() for p in self.presence.values()]
        })

        # Broadcast user joined
        await self._broadcast({
            "type": "user_joined",
            "user": user.to_dict()
        }, exclude=user.user_id)

        logger.info(f"User {user.username} joined document {self.document_id}")

    async def leave(self, user_id: str):
        """Remove a client from the session."""
        async with self._lock:
            self.clients.pop(user_id, None)
            user = self.presence.pop(user_id, None)

        if user:
            await self._broadcast({
                "type": "user_left",
                "user_id": user_id,
                "username": user.username
            })
            logger.info(f"User {user.username} left document {self.document_id}")

    async def apply_operation(self, operation: Operation) -> Optional[Operation]:
        """
        Apply an operation to the document.

        Transforms the operation against any concurrent operations
        and returns the transformed operation.
        """
        async with self._lock:
            # Transform against any operations since the client's version
            transformed_op = operation
            for hist_op in self.operation_history[operation.version:]:
                transformed_op = self.ot.transform(transformed_op, hist_op)

            # Apply the operation
            if transformed_op.op_type == OperationType.INSERT:
                self.content = (
                    self.content[:transformed_op.position] +
                    transformed_op.content +
                    self.content[transformed_op.position:]
                )
            elif transformed_op.op_type == OperationType.DELETE:
                self.content = (
                    self.content[:transformed_op.position] +
                    self.content[transformed_op.position + transformed_op.length:]
                )

            # Update version and history
            self.version += 1
            transformed_op.version = self.version
            self.operation_history.append(transformed_op)

            # Trim history if too large
            if len(self.operation_history) > self.max_history_size:
                self.operation_history = self.operation_history[-self.max_history_size // 2:]

        # Broadcast the operation
        await self._broadcast({
            "type": "operation",
            "operation": transformed_op.to_dict(),
            "version": self.version
        }, exclude=operation.user_id)

        # Acknowledge to sender
        if operation.user_id in self.clients:
            await self._send_to_client(self.clients[operation.user_id], {
                "type": "ack",
                "version": self.version
            })

        return transformed_op

    async def update_presence(self, user_id: str, cursor_position: int,
                              selection_start: int = 0, selection_end: int = 0):
        """Update user presence information."""
        if user_id in self.presence:
            self.presence[user_id].cursor_position = cursor_position
            self.presence[user_id].selection_start = selection_start
            self.presence[user_id].selection_end = selection_end
            self.presence[user_id].last_active = time.time()

            await self._broadcast({
                "type": "presence",
                "user_id": user_id,
                "cursor_position": cursor_position,
                "selection_start": selection_start,
                "selection_end": selection_end
            }, exclude=user_id)

    async def _broadcast(self, message: Dict[str, Any], exclude: Optional[str] = None):
        """Broadcast a message to all clients except the excluded one."""
        payload = json.dumps(message)
        tasks = [
            client.send(payload)
            for user_id, client in self.clients.items()
            if user_id != exclude
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_to_client(self, websocket: WebSocketServerProtocol,
                              message: Dict[str, Any]):
        """Send a message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "document_id": self.document_id,
            "content_length": len(self.content),
            "version": self.version,
            "active_users": len(self.clients),
            "operation_count": len(self.operation_history)
        }


class CollaborationServer:
    """
    WebSocket server for real-time collaborative editing.

    Manages multiple document sessions and handles client connections.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.sessions: Dict[str, DocumentSession] = {}
        self.user_colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
            "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
        ]
        self._color_index = 0

    def _get_next_color(self) -> str:
        """Get the next user color."""
        color = self.user_colors[self._color_index % len(self.user_colors)]
        self._color_index += 1
        return color

    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a WebSocket connection."""
        user_id = None
        document_id = None

    async def handler(
        self, websocket: websockets.WebSocketServerProtocol, path: str
    ) -> None:  # noqa: ARG002
        doc_id = websocket.request_headers.get("x-document-id", "default")
        session = self.sessions.setdefault(doc_id, DocumentSession())
        session.clients.add(websocket)
        await websocket.send(json.dumps({"type": "snapshot", "text": session.text}))
        try:
            # Get authentication and document info from headers or first message
            auth_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            auth_data = json.loads(auth_message)

            document_id = auth_data.get("document_id", "default")
            user_id = auth_data.get("user_id", str(uuid.uuid4()))
            username = auth_data.get("username", f"User-{user_id[:8]}")

            # Get or create session
            if document_id not in self.sessions:
                self.sessions[document_id] = DocumentSession(document_id)

            session = self.sessions[document_id]

            # Create user presence
            user = UserPresence(
                user_id=user_id,
                username=username,
                color=self._get_next_color()
            )

            # Join the session
            await session.join(websocket, user)

            # Handle messages
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
            # Clean up
            if user_id and document_id and document_id in self.sessions:
                await self.sessions[document_id].leave(user_id)

                # Remove empty sessions
                if not self.sessions[document_id].clients:
                    # Keep session for a while in case users reconnect
                    pass

    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting collaboration server on {self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # Run forever

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            "active_sessions": len(self.sessions),
            "total_users": sum(len(s.clients) for s in self.sessions.values()),
            "sessions": [s.get_stats() for s in self.sessions.values()]
        }


async def main():
    """Main entry point."""
    server = CollaborationServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
