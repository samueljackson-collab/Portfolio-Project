"""Test Lambda functions."""
import pytest
import json

def test_create_event_structure():
    """Test event structure for create function."""
    event = {
        'body': json.dumps({'name': 'Test Item', 'description': 'Test'})
    }
    assert 'body' in event
    body = json.loads(event['body'])
    assert 'name' in body
