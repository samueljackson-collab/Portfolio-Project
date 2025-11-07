#!/usr/bin/env python3
"""Simple HA web application."""
from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'hostname': socket.gethostname()})

@app.route('/ready')
def ready():
    """Readiness check endpoint."""
    return jsonify({'status': 'ready', 'hostname': socket.gethostname()})

@app.route('/')
def index():
    """Main endpoint."""
    return jsonify({
        'message': 'Hello from HA Web App',
        'hostname': socket.gethostname(),
        'pid': os.getpid()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
