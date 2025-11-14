"""
Tests for Native Messaging Host
"""

import asyncio
import json
import struct
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from io import BytesIO

# Import the module under test
sys.path.insert(0, '..')
from native_host import NativeMessagingHost


class TestNativeMessagingHost(unittest.TestCase):
    """Test cases for Native Messaging Host"""

    def setUp(self):
        """Set up test fixtures"""
        self.host = NativeMessagingHost()

    @patch('websockets.connect')
    async def test_connect_to_app_success(self, mock_connect):
        """Test successful connection to Flutter app"""
        mock_websocket = AsyncMock()
        mock_connect.return_value = mock_websocket

        result = await self.host.connect_to_app()

        self.assertTrue(result)
        self.assertEqual(self.host.websocket, mock_websocket)
        mock_connect.assert_called_once_with('ws://localhost:8765')

    @patch('websockets.connect')
    async def test_connect_to_app_failure(self, mock_connect):
        """Test failed connection to Flutter app"""
        mock_connect.side_effect = Exception('Connection failed')

        result = await self.host.connect_to_app()

        self.assertFalse(result)
        self.assertIsNone(self.host.websocket)

    def test_read_message_valid(self):
        """Test reading valid message from browser"""
        test_message = {'type': 'test', 'data': 'value'}
        encoded_message = json.dumps(test_message).encode('utf-8')
        message_length = struct.pack('=I', len(encoded_message))

        # Mock stdin
        mock_stdin = BytesIO(message_length + encoded_message)
        with patch('sys.stdin', Mock(buffer=mock_stdin)):
            result = self.host.read_message()

        self.assertEqual(result, test_message)

    def test_read_message_empty(self):
        """Test reading empty message (EOF)"""
        mock_stdin = BytesIO(b'')
        with patch('sys.stdin', Mock(buffer=mock_stdin)):
            result = self.host.read_message()

        self.assertIsNone(result)

    def test_read_message_invalid_json(self):
        """Test reading invalid JSON message"""
        invalid_json = b'invalid json'
        message_length = struct.pack('=I', len(invalid_json))

        mock_stdin = BytesIO(message_length + invalid_json)
        with patch('sys.stdin', Mock(buffer=mock_stdin)):
            result = self.host.read_message()

        self.assertIsNone(result)

    def test_send_message(self):
        """Test sending message to browser"""
        test_message = {'type': 'response', 'status': 'ok'}

        mock_stdout = BytesIO()
        with patch('sys.stdout', Mock(buffer=mock_stdout)):
            self.host.send_message(test_message)

        mock_stdout.seek(0)
        length_bytes = mock_stdout.read(4)
        message_length = struct.unpack('=I', length_bytes)[0]
        message_bytes = mock_stdout.read(message_length)
        decoded_message = json.loads(message_bytes.decode('utf-8'))

        self.assertEqual(decoded_message, test_message)

    def test_send_message_error_handling(self):
        """Test error handling in send_message"""
        test_message = {'type': 'test'}

        with patch('sys.stdout', Mock(buffer=Mock(write=Mock(side_effect=Exception('Write failed'))))):
            # Should not raise exception
            self.host.send_message(test_message)

    async def test_forward_to_app_success(self):
        """Test forwarding message to app"""
        test_message = {'type': 'tabs_update', 'tabs': []}

        mock_websocket = AsyncMock()
        self.host.websocket = mock_websocket

        await self.host.forward_to_app(test_message)

        mock_websocket.send.assert_called_once_with(json.dumps(test_message))

    async def test_forward_to_app_not_connected(self):
        """Test forwarding when not connected"""
        test_message = {'type': 'test'}
        self.host.websocket = None

        # Should not raise exception
        await self.host.forward_to_app(test_message)

    async def test_forward_to_app_error(self):
        """Test error handling in forward_to_app"""
        test_message = {'type': 'test'}

        mock_websocket = AsyncMock()
        mock_websocket.send.side_effect = Exception('Send failed')
        self.host.websocket = mock_websocket

        # Should not raise exception
        await self.host.forward_to_app(test_message)

    async def test_handle_browser_message_connect(self):
        """Test handling connect message from browser"""
        connect_message = {'type': 'connect', 'timestamp': 1234567890}

        with patch.object(self.host, 'send_message') as mock_send:
            await self.host.handle_browser_message(connect_message)

            mock_send.assert_called_once()
            sent_message = mock_send.call_args[0][0]
            self.assertEqual(sent_message['type'], 'connected')
            self.assertEqual(sent_message['status'], 'ok')

    async def test_handle_browser_message_tabs_update(self):
        """Test handling tabs_update message"""
        tabs_message = {'type': 'tabs_update', 'tabs': [{'id': '1', 'url': 'https://example.com'}]}

        with patch.object(self.host, 'forward_to_app') as mock_forward:
            await self.host.handle_browser_message(tabs_message)

            mock_forward.assert_called_once_with(tabs_message)

    async def test_handle_browser_message_tab_closed(self):
        """Test handling tab_closed message"""
        closed_message = {'type': 'tab_closed', 'tab_id': '123'}

        with patch.object(self.host, 'forward_to_app') as mock_forward:
            await self.host.handle_browser_message(closed_message)

            mock_forward.assert_called_once_with(closed_message)

    async def test_handle_browser_message_organize_request(self):
        """Test handling organize_request message"""
        organize_message = {'type': 'organize_request'}

        with patch.object(self.host, 'forward_to_app') as mock_forward:
            await self.host.handle_browser_message(organize_message)

            mock_forward.assert_called_once_with(organize_message)

    async def test_handle_browser_message_unknown_type(self):
        """Test handling unknown message type"""
        unknown_message = {'type': 'unknown_message_type', 'data': 'value'}

        # Should not raise exception
        await self.host.handle_browser_message(unknown_message)

    async def test_handle_app_message(self):
        """Test handling messages from app"""
        test_message = json.dumps({'type': 'classification_result', 'category': 'work'})

        mock_websocket = AsyncMock()
        mock_websocket.__aiter__.return_value = [test_message]
        self.host.websocket = mock_websocket

        with patch.object(self.host, 'send_message') as mock_send:
            await self.host.handle_app_message()

            mock_send.assert_called_once()
            sent_message = mock_send.call_args[0][0]
            self.assertEqual(sent_message['type'], 'classification_result')

    async def test_handle_app_message_invalid_json(self):
        """Test handling invalid JSON from app"""
        mock_websocket = AsyncMock()
        mock_websocket.__aiter__.return_value = ['invalid json']
        self.host.websocket = mock_websocket

        # Should not raise exception
        await self.host.handle_app_message()

    async def test_handle_app_message_error(self):
        """Test error handling in handle_app_message"""
        mock_websocket = AsyncMock()
        mock_websocket.__aiter__.side_effect = Exception('WebSocket error')
        self.host.websocket = mock_websocket

        # Should not raise exception
        await self.host.handle_app_message()

    @patch.object(NativeMessagingHost, 'connect_to_app')
    @patch.object(NativeMessagingHost, 'read_message')
    @patch.object(NativeMessagingHost, 'handle_browser_message')
    async def test_run_main_loop(self, mock_handle, mock_read, mock_connect):
        """Test main run loop"""
        mock_connect.return_value = True
        mock_read.side_effect = [
            {'type': 'test1'},
            {'type': 'test2'},
            None,  # Simulate browser disconnect
        ]

        await self.host.run()

        mock_connect.assert_called_once()
        self.assertEqual(mock_handle.call_count, 2)

    @patch.object(NativeMessagingHost, 'connect_to_app')
    async def test_run_connection_failure(self, mock_connect):
        """Test run loop when connection fails"""
        mock_connect.return_value = False

        await self.host.run()

        # Should exit gracefully
        mock_connect.assert_called_once()

    @patch.object(NativeMessagingHost, 'connect_to_app')
    @patch.object(NativeMessagingHost, 'read_message')
    async def test_run_keyboard_interrupt(self, mock_read, mock_connect):
        """Test handling KeyboardInterrupt"""
        mock_connect.return_value = True
        mock_read.side_effect = KeyboardInterrupt()

        await self.host.run()

        # Should exit gracefully
        self.assertFalse(self.host.running)


class TestNativeHostIntegration(unittest.TestCase):
    """Integration tests for Native Messaging Host"""

    def test_message_protocol_integrity(self):
        """Test that message encoding/decoding is symmetric"""
        host = NativeMessagingHost()
        test_message = {
            'type': 'test',
            'data': {'nested': 'value'},
            'array': [1, 2, 3],
        }

        # Encode message
        encoded_message = json.dumps(test_message).encode('utf-8')
        message_length = struct.pack('=I', len(encoded_message))

        # Simulate sending and receiving
        mock_buffer = BytesIO(message_length + encoded_message)
        with patch('sys.stdin', Mock(buffer=mock_buffer)):
            received_message = host.read_message()

        self.assertEqual(received_message, test_message)

    def test_large_message_handling(self):
        """Test handling of large messages"""
        host = NativeMessagingHost()
        
        # Create large message (10K items)
        large_message = {
            'type': 'tabs_update',
            'tabs': [{'id': str(i), 'url': f'https://example{i}.com'} for i in range(10000)]
        }

        # Encode
        encoded_message = json.dumps(large_message).encode('utf-8')
        message_length = struct.pack('=I', len(encoded_message))

        # Simulate receiving
        mock_buffer = BytesIO(message_length + encoded_message)
        with patch('sys.stdin', Mock(buffer=mock_buffer)):
            received_message = host.read_message()

        self.assertEqual(len(received_message['tabs']), 10000)

    def test_unicode_message_handling(self):
        """Test handling of Unicode in messages"""
        host = NativeMessagingHost()
        
        unicode_message = {
            'type': 'test',
            'title': '日本語のタイトル',
            'emoji': '🚀🌟',
        }

        encoded_message = json.dumps(unicode_message).encode('utf-8')
        message_length = struct.pack('=I', len(encoded_message))

        mock_buffer = BytesIO(message_length + encoded_message)
        with patch('sys.stdin', Mock(buffer=mock_buffer)):
            received_message = host.read_message()

        self.assertEqual(received_message['title'], '日本語のタイトル')
        self.assertEqual(received_message['emoji'], '🚀🌟')


class TestNativeHostEdgeCases(unittest.TestCase):
    """Edge case tests for Native Messaging Host"""

    def test_empty_message(self):
        """Test handling empty message"""
        host = NativeMessagingHost()
        empty_message = {}

        # Should handle gracefully
        mock_stdout = BytesIO()
        with patch('sys.stdout', Mock(buffer=mock_stdout)):
            host.send_message(empty_message)

        mock_stdout.seek(0)
        length_bytes = mock_stdout.read(4)
        message_length = struct.unpack('=I', length_bytes)[0]
        
        self.assertGreater(message_length, 0)

    def test_message_with_null_values(self):
        """Test handling messages with null values"""
        host = NativeMessagingHost()
        
        null_message = {
            'type': 'test',
            'value': None,
            'nested': {'null': None}
        }

        encoded_message = json.dumps(null_message).encode('utf-8')
        message_length = struct.pack('=I', len(encoded_message))

        mock_buffer = BytesIO(message_length + encoded_message)
        with patch('sys.stdin', Mock(buffer=mock_buffer)):
            received_message = host.read_message()

        self.assertIsNone(received_message['value'])
        self.assertIsNone(received_message['nested']['null'])

    def test_malformed_length_prefix(self):
        """Test handling malformed message length"""
        host = NativeMessagingHost()
        
        # Only 3 bytes instead of 4
        malformed = b'\x01\x02\x03'
        
        mock_buffer = BytesIO(malformed)
        with patch('sys.stdin', Mock(buffer=mock_buffer)):
            result = host.read_message()

        self.assertIsNone(result)

    def test_truncated_message(self):
        """Test handling truncated message"""
        host = NativeMessagingHost()
        
        # Length says 100 bytes, but only provide 10
        fake_length = struct.pack('=I', 100)
        short_data = b'short'
        
        mock_buffer = BytesIO(fake_length + short_data)
        with patch('sys.stdin', Mock(buffer=mock_buffer)):
            result = host.read_message()

        # Should handle gracefully
        self.assertIsNone(result)


def async_test(coro):
    """Decorator to run async tests"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper


# Apply async_test decorator to async test methods
for attr_name in dir(TestNativeMessagingHost):
    if attr_name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestNativeMessagingHost, attr_name)):
        setattr(TestNativeMessagingHost, attr_name, async_test(getattr(TestNativeMessagingHost, attr_name)))


if __name__ == '__main__':
    unittest.main()