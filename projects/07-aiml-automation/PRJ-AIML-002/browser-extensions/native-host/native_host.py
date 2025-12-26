#!/usr/bin/env python3
"""
Native Messaging Host for Tab Organizer
Bridges browser extensions with the Flutter desktop app
"""

import asyncio
import json
import struct
import sys
import logging
from typing import Dict, Any
import websockets

# Configuration
WEBSOCKET_HOST = 'localhost'
WEBSOCKET_PORT = 8765
LOG_FILE = '/tmp/tab_organizer_native_host.log'

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class NativeMessagingHost:
    """Native messaging host for browser communication"""

    def __init__(self):
        self.websocket = None
        self.running = True

    async def connect_to_app(self):
        """Connect to Flutter desktop app via WebSocket"""
        try:
            uri = f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"
            self.websocket = await websockets.connect(uri)
            logger.info(f"Connected to app at {uri}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to app: {e}")
            return False

    def read_message(self) -> Dict[str, Any]:
        """Read message from browser using native messaging protocol"""
        try:
            # Read message length (4 bytes)
            raw_length = sys.stdin.buffer.read(4)
            if not raw_length:
                return None

            message_length = struct.unpack('=I', raw_length)[0]

            # Read message content
            message = sys.stdin.buffer.read(message_length).decode('utf-8')
            return json.loads(message)

        except Exception as e:
            logger.error(f"Failed to read message: {e}")
            return None

    def send_message(self, message: Dict[str, Any]):
        """Send message to browser using native messaging protocol"""
        try:
            encoded_content = json.dumps(message).encode('utf-8')
            encoded_length = struct.pack('=I', len(encoded_content))

            sys.stdout.buffer.write(encoded_length)
            sys.stdout.buffer.write(encoded_content)
            sys.stdout.buffer.flush()

            logger.debug(f"Sent message to browser: {message.get('type')}")

        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def forward_to_app(self, message: Dict[str, Any]):
        """Forward message from browser to app"""
        if not self.websocket:
            logger.warning("Not connected to app")
            return

        try:
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Forwarded to app: {message.get('type')}")
        except Exception as e:
            logger.error(f"Failed to forward to app: {e}")

    async def handle_browser_message(self, message: Dict[str, Any]):
        """Handle message from browser"""
        msg_type = message.get('type')
        logger.info(f"Received from browser: {msg_type}")

        if msg_type == 'connect':
            # Browser is connecting
            self.send_message({
                'type': 'connected',
                'status': 'ok',
                'timestamp': message.get('timestamp')
            })

        elif msg_type == 'tabs_update':
            # Forward tab updates to app
            await self.forward_to_app(message)

        elif msg_type == 'tab_closed':
            # Forward tab closure to app
            await self.forward_to_app(message)

        elif msg_type == 'organize_request':
            # Request to organize tabs
            await self.forward_to_app(message)

        elif msg_type == 'open_app':
            # Request to open the desktop app
            await self.forward_to_app(message)

        else:
            logger.warning(f"Unknown message type: {msg_type}")

    async def handle_app_message(self):
        """Handle messages from app"""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                msg_type = data.get('type')
                logger.info(f"Received from app: {msg_type}")

                # Forward to browser
                self.send_message(data)

        except Exception as e:
            logger.error(f"Error handling app message: {e}")

    async def run(self):
        """Main run loop"""
        logger.info("Native messaging host starting")

        # Connect to app
        connected = await self.connect_to_app()
        if not connected:
            logger.error("Failed to connect to app, exiting")
            return

        # Start listening to app messages
        app_task = asyncio.create_task(self.handle_app_message())

        try:
            # Handle browser messages
            while self.running:
                message = self.read_message()
                if message is None:
                    logger.info("Browser disconnected")
                    break

                await self.handle_browser_message(message)

                # Small delay to prevent busy loop
                await asyncio.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.running = False
            app_task.cancel()

            if self.websocket:
                await self.websocket.close()

            logger.info("Native messaging host stopped")


def main():
    """Entry point"""
    try:
        host = NativeMessagingHost()
        asyncio.run(host.run())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
