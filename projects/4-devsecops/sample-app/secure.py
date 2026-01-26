#!/usr/bin/env python3
"""
SECURE APPLICATION - Demonstrates security best practices

This file shows the corrected versions of vulnerabilities from vulnerable.py.
Each fix is annotated with the security improvement made.
"""

import hashlib
import ipaddress
import logging
import os
import secrets
import shlex
import subprocess
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

import bcrypt
from flask import Flask, request, render_template, redirect, url_for, abort
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from markupsafe import escape
import defusedxml.ElementTree as ET

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# FIX: Use environment variables for secrets (CWE-798)
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
API_KEY = os.environ.get('API_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# FIX: Enforce HTTPS with security headers
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'"
})

# FIX: Rate limiting to prevent brute force
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# FIX: Use parameterized queries (CWE-89)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ.get('DATABASE_URL', 'sqlite:///app.db'))
Session = sessionmaker(bind=engine)


@app.route('/user')
@limiter.limit("10 per minute")
def get_user():
    user_id = request.args.get('id')

    # FIX: Validate input type
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        abort(400, "Invalid user ID")

    # FIX: Use parameterized query
    session = Session()
    try:
        result = session.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        return str(result.fetchall())
    finally:
        session.close()


# FIX: Prevent command injection (CWE-78)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'google.com', 'github.com']


@app.route('/ping')
@limiter.limit("5 per minute")
def ping_host():
    host = request.args.get('host', '')

    # FIX: Validate against allowlist
    if host not in ALLOWED_HOSTS:
        abort(400, "Host not allowed")

    # FIX: Use list form to avoid shell injection
    try:
        result = subprocess.run(
            ['ping', '-c', '1', host],
            capture_output=True,
            timeout=5,
            check=False
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        abort(504, "Ping timeout")


# FIX: Prevent path traversal (CWE-22)
SAFE_DIRECTORY = Path('/var/data').resolve()


@app.route('/file')
@limiter.limit("10 per minute")
def read_file():
    filename = request.args.get('name', '')

    # FIX: Sanitize and validate file path
    if not filename or '..' in filename or filename.startswith('/'):
        abort(400, "Invalid filename")

    filepath = (SAFE_DIRECTORY / filename).resolve()

    # FIX: Ensure path is within allowed directory
    if not str(filepath).startswith(str(SAFE_DIRECTORY)):
        abort(403, "Access denied")

    if not filepath.is_file():
        abort(404, "File not found")

    with open(filepath, 'r') as f:
        return f.read()


# FIX: Prevent XSS (CWE-79)
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    # FIX: Use proper escaping via template
    safe_name = escape(name)
    return render_template('greet.html', name=safe_name)


# FIX: Avoid insecure deserialization (CWE-502)
import json


@app.route('/load', methods=['POST'])
@limiter.limit("5 per minute")
def load_data():
    # FIX: Use JSON instead of pickle for untrusted data
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            abort(400, "Invalid data format")
        return str(data)
    except Exception:
        abort(400, "Invalid JSON")


# FIX: Use strong cryptography (CWE-327)
def hash_password(password: str) -> str:
    # FIX: Use bcrypt with automatic salting
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# FIX: Use cryptographically secure random (CWE-330)
def generate_token() -> str:
    # FIX: Use secrets module for security tokens
    return secrets.token_hex(32)


# FIX: Prevent open redirect (CWE-601)
ALLOWED_REDIRECT_HOSTS = ['example.com', 'www.example.com']


@app.route('/redirect')
def safe_redirect():
    url = request.args.get('url', '/')

    # FIX: Validate redirect URL
    parsed = urlparse(url)

    # Only allow relative URLs or approved hosts
    if parsed.netloc and parsed.netloc not in ALLOWED_REDIRECT_HOSTS:
        logger.warning(f"Blocked redirect attempt to: {url}")
        abort(400, "Invalid redirect URL")

    return redirect(url)


# FIX: Prevent XXE (CWE-611)
def parse_xml(xml_file):
    # FIX: Use defusedxml which disables dangerous features
    tree = ET.parse(xml_file)
    return tree.getroot()


# FIX: Prevent SSRF (CWE-918)
import requests
from urllib.parse import urlparse

ALLOWED_FETCH_DOMAINS = ['api.example.com', 'cdn.example.com']


@app.route('/fetch')
@limiter.limit("5 per minute")
def fetch_url():
    url = request.args.get('url', '')

    # FIX: Validate URL against allowlist
    parsed = urlparse(url)

    if not parsed.scheme in ('http', 'https'):
        abort(400, "Invalid URL scheme")

    if parsed.netloc not in ALLOWED_FETCH_DOMAINS:
        logger.warning(f"Blocked SSRF attempt to: {url}")
        abort(403, "Domain not allowed")

    # FIX: Block private IP ranges
    try:
        import socket
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            abort(403, "Private IPs not allowed")
    except socket.gaierror:
        abort(400, "Invalid hostname")

    response = requests.get(url, timeout=5)
    return response.text


# FIX: Use configuration from environment
ADMIN_SERVER = os.environ.get('ADMIN_SERVER')
DATABASE_HOST = os.environ.get('DATABASE_HOST')

# FIX: Disable debug mode in production (CWE-489)
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
TESTING = os.environ.get('FLASK_TESTING', 'false').lower() == 'true'


# FIX: Secure login with proper logging and timing-safe comparison
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # FIX: Log authentication attempts
    logger.info(f"Login attempt for user: {username}")

    # FIX: Use timing-safe comparison
    stored_hash = get_password_hash(username)  # From database
    if stored_hash and secrets.compare_digest(
        hash_password(password),
        stored_hash
    ):
        logger.info(f"Successful login for user: {username}")
        return "Login successful"

    logger.warning(f"Failed login attempt for user: {username}")
    return "Login failed", 401


def get_password_hash(username: str) -> str:
    """Get password hash from database (placeholder)."""
    # In real app, query database for user's password hash
    return None


# FIX: Proper logging for security events (CWE-778)
def process_payment(card_number: str, amount: float) -> bool:
    # Mask card number for logging
    masked_card = f"****-****-****-{card_number[-4:]}"
    logger.info(f"Processing payment: amount={amount}, card={masked_card}")

    try:
        # Process payment...
        result = True
        logger.info(f"Payment successful: amount={amount}, card={masked_card}")
        return result
    except Exception as e:
        logger.error(f"Payment failed: amount={amount}, card={masked_card}, error={e}")
        raise


# FIX: Thread-safe operations (CWE-362)
import threading

balance_lock = threading.Lock()
balance = 1000


def withdraw(amount: float) -> bool:
    # FIX: Use lock for atomic operations
    with balance_lock:
        global balance
        if balance >= amount:
            balance -= amount
            logger.info(f"Withdrawal successful: amount={amount}, new_balance={balance}")
            return True
        logger.warning(f"Withdrawal failed: insufficient funds, amount={amount}")
        return False


if __name__ == '__main__':
    # FIX: Don't run with debug in production
    app.run(
        debug=DEBUG,
        host='127.0.0.1',  # Don't bind to 0.0.0.0 by default
        port=int(os.environ.get('PORT', 5000))
    )
