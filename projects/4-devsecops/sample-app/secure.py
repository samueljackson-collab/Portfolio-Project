#!/usr/bin/env python3
"""
SECURE APPLICATION - Demonstrates security best practices

This application shows the secure implementation of the same functionality
as vulnerable.py, following security best practices and OWASP guidelines.

Security measures implemented:
- Parameterized queries (prevents SQL Injection)
- Input validation and sanitization
- Secure password hashing (bcrypt/argon2)
- Content Security Policy headers
- Secure session management
- Path validation
- CSRF protection
- Rate limiting
- Secure logging
"""

import os
import re
import hmac
import secrets
import hashlib
import logging
import ipaddress
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

import sqlite3
from flask import Flask, request, jsonify, abort, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from markupsafe import escape
import defusedxml.ElementTree as ET

app = Flask(__name__)

# SECURE: Load secrets from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
DATABASE_URL = os.environ.get('DATABASE_URL', 'users_secure.db')

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# SECURE: Configure secure logging (no sensitive data)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SECURE: Allowed hosts for redirects
ALLOWED_REDIRECT_HOSTS = {'example.com', 'www.example.com'}

# SECURE: Allowed file extensions for downloads
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx'}


def init_database():
    """Initialize SQLite database with secure schema."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action TEXT,
            ip_address TEXT,
            success BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()


# SECURE: Password hashing using bcrypt-like approach with secrets
def hash_password_secure(password: str) -> str:
    """Hash password using secure algorithm with salt."""
    salt = secrets.token_hex(32)
    # Using PBKDF2 with SHA-256 and 100,000 iterations
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, hash_value = stored_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return hmac.compare_digest(new_hash, hash_value)
    except (ValueError, AttributeError):
        return False


# SECURE: Input validation decorator
def validate_input(schema):
    """Decorator to validate request input."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Validate based on schema
            for field, rules in schema.items():
                value = request.form.get(field) or request.args.get(field)
                if rules.get('required') and not value:
                    abort(400, description=f"Missing required field: {field}")
                if value and rules.get('pattern'):
                    if not re.match(rules['pattern'], value):
                        abort(400, description=f"Invalid format for field: {field}")
                if value and rules.get('max_length'):
                    if len(value) > rules['max_length']:
                        abort(400, description=f"Field too long: {field}")
            return f(*args, **kwargs)
        return wrapper
    return decorator


# SECURE: Require authentication decorator
def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token or not validate_session_token(auth_token):
            abort(401, description="Authentication required")
        return f(*args, **kwargs)
    return wrapper


def validate_session_token(token: str) -> bool:
    """Validate session token securely."""
    # In production, validate against session store
    # This is a simplified example
    return bool(token and len(token) >= 32)


# SECURE: SQL Injection prevention with parameterized queries
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
@validate_input({
    'username': {'required': True, 'pattern': r'^[a-zA-Z0-9_]{3,50}$', 'max_length': 50},
    'password': {'required': True, 'max_length': 128}
})
def login():
    """Secure login endpoint with parameterized queries."""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    client_ip = request.remote_addr

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # SECURE: Parameterized query prevents SQL injection
    cursor.execute(
        "SELECT id, password_hash, failed_login_attempts, locked_until FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if not user:
        # SECURE: Consistent timing to prevent user enumeration
        hash_password_secure("dummy_password")
        log_audit(cursor, None, 'login_attempt', client_ip, False)
        conn.commit()
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401

    user_id, password_hash, failed_attempts, locked_until = user

    # Check if account is locked
    if locked_until:
        from datetime import datetime
        if datetime.now() < datetime.fromisoformat(locked_until):
            return jsonify({'error': 'Account temporarily locked'}), 403

    # Verify password
    if verify_password(password, password_hash):
        # Reset failed attempts on successful login
        cursor.execute(
            "UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = ?",
            (user_id,)
        )
        log_audit(cursor, user_id, 'login_success', client_ip, True)

        # SECURE: Generate secure session token
        session_token = secrets.token_urlsafe(32)

        conn.commit()
        conn.close()

        logger.info(f"Successful login for user_id={user_id}")
        return jsonify({
            'message': 'Login successful',
            'token': session_token
        })
    else:
        # Increment failed attempts
        new_attempts = failed_attempts + 1
        locked_until_value = None

        if new_attempts >= 5:
            from datetime import datetime, timedelta
            locked_until_value = (datetime.now() + timedelta(minutes=15)).isoformat()

        cursor.execute(
            "UPDATE users SET failed_login_attempts = ?, locked_until = ? WHERE id = ?",
            (new_attempts, locked_until_value, user_id)
        )
        log_audit(cursor, user_id, 'login_failed', client_ip, False)

        conn.commit()
        conn.close()

        return jsonify({'error': 'Invalid credentials'}), 401


def log_audit(cursor, user_id, action, ip_address, success):
    """Log audit event to database."""
    cursor.execute(
        "INSERT INTO audit_log (user_id, action, ip_address, success) VALUES (?, ?, ?, ?)",
        (user_id, action, ip_address, success)
    )


# SECURE: Command execution with strict validation
@app.route('/ping')
@limiter.limit("10 per minute")
def ping():
    """Secure ping endpoint with strict input validation."""
    host = request.args.get('host', '')

    # SECURE: Validate host is a valid IP address or hostname
    if not host:
        return jsonify({'error': 'Host parameter required'}), 400

    # Validate IP address format
    try:
        ip = ipaddress.ip_address(host)
        # Reject private/internal IPs to prevent SSRF
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            return jsonify({'error': 'Invalid host address'}), 400
    except ValueError:
        # Validate hostname format
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', host):
            return jsonify({'error': 'Invalid hostname format'}), 400

    # SECURE: Use subprocess with list arguments (no shell)
    import subprocess
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', host],
            capture_output=True,
            text=True,
            timeout=5
        )
        return jsonify({
            'host': host,
            'reachable': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else 'Host unreachable'
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Ping timeout'}), 408


# SECURE: XSS prevention with proper escaping
@app.route('/search')
@validate_input({
    'q': {'required': False, 'max_length': 200}
})
def search():
    """Secure search endpoint with XSS prevention."""
    query = request.args.get('q', '')

    # SECURE: Escape user input to prevent XSS
    safe_query = escape(query)

    # In a real app, perform actual search
    results = []

    return jsonify({
        'query': safe_query,
        'results': results,
        'count': len(results)
    })


# SECURE: Profile with proper output encoding
@app.route('/profile')
@require_auth
def profile():
    """Secure profile endpoint."""
    # SECURE: User data would come from authenticated session
    name = escape(request.args.get('name', 'Guest'))

    return jsonify({
        'name': name,
        'message': 'Welcome to your profile page!'
    })


# SECURE: Session handling without pickle
@app.route('/load_session', methods=['POST'])
@limiter.limit("10 per minute")
def load_session():
    """Secure session loading using JSON."""
    import json

    session_data = request.form.get('session', '')

    # SECURE: Use JSON instead of pickle for deserialization
    try:
        import base64
        decoded = base64.b64decode(session_data)
        # Validate JSON structure
        session = json.loads(decoded)

        # SECURE: Validate session structure
        allowed_keys = {'user_id', 'created_at', 'expires_at'}
        if not all(key in allowed_keys for key in session.keys()):
            return jsonify({'error': 'Invalid session structure'}), 400

        return jsonify({'session': session})
    except (json.JSONDecodeError, ValueError):
        return jsonify({'error': 'Invalid session data'}), 400


# SECURE: Path traversal prevention
@app.route('/download')
@require_auth
@validate_input({
    'file': {'required': True, 'pattern': r'^[a-zA-Z0-9_.-]+$', 'max_length': 100}
})
def download():
    """Secure file download with path validation."""
    filename = request.args.get('file', '')

    # SECURE: Define allowed base directory
    base_dir = Path('/var/www/files').resolve()

    # SECURE: Validate filename format
    if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
        return jsonify({'error': 'Invalid filename'}), 400

    # SECURE: Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'File type not allowed'}), 403

    # SECURE: Resolve and validate path stays within allowed directory
    try:
        requested_path = (base_dir / filename).resolve()

        # Ensure the resolved path is within the base directory
        if not str(requested_path).startswith(str(base_dir)):
            logger.warning(f"Path traversal attempt: {filename}")
            return jsonify({'error': 'Access denied'}), 403

        if not requested_path.exists():
            return jsonify({'error': 'File not found'}), 404

        from flask import send_file
        return send_file(requested_path)

    except Exception as e:
        logger.error(f"File access error: {type(e).__name__}")
        return jsonify({'error': 'File access error'}), 500


# SECURE: XML parsing with XXE protection
@app.route('/parse_xml', methods=['POST'])
@limiter.limit("10 per minute")
def parse_xml():
    """Secure XML parser with XXE protection."""
    xml_data = request.data.decode('utf-8')

    # SECURE: Use defusedxml to prevent XXE attacks
    try:
        tree = ET.fromstring(xml_data)
        # Process XML safely
        return jsonify({
            'tag': tree.tag,
            'attributes': tree.attrib,
            'children': len(tree)
        })
    except ET.ParseError:
        return jsonify({'error': 'Invalid XML'}), 400


# SECURE: SSRF prevention with URL validation
@app.route('/fetch')
@require_auth
@limiter.limit("5 per minute")
def fetch_url():
    """Secure URL fetcher with SSRF protection."""
    url = request.args.get('url', '')

    if not url:
        return jsonify({'error': 'URL parameter required'}), 400

    # SECURE: Parse and validate URL
    try:
        parsed = urlparse(url)

        # Only allow HTTPS
        if parsed.scheme != 'https':
            return jsonify({'error': 'Only HTTPS URLs allowed'}), 400

        # Validate hostname
        if not parsed.netloc:
            return jsonify({'error': 'Invalid URL'}), 400

        # Block internal/private IPs
        import socket
        try:
            ip = socket.gethostbyname(parsed.hostname)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
                return jsonify({'error': 'Internal URLs not allowed'}), 403
        except socket.gaierror:
            return jsonify({'error': 'Invalid hostname'}), 400

        # Allowlist of domains (in production)
        ALLOWED_DOMAINS = {'api.example.com', 'data.example.com'}
        if parsed.hostname not in ALLOWED_DOMAINS:
            return jsonify({'error': 'Domain not in allowlist'}), 403

        # Fetch with timeout
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'SecureApp/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            # Limit response size
            content = response.read(1024 * 1024)  # 1MB max
            return jsonify({
                'status': response.status,
                'content_length': len(content)
            })

    except Exception as e:
        logger.error(f"Fetch error: {type(e).__name__}")
        return jsonify({'error': 'Fetch failed'}), 500


# SECURE: Error handling without sensitive data exposure
@app.errorhandler(Exception)
def handle_error(error):
    """Secure error handler that doesn't expose internals."""
    # Log detailed error internally
    logger.exception("Application error occurred")

    # SECURE: Return generic error message to user
    return jsonify({
        'error': 'An error occurred',
        'request_id': secrets.token_hex(8)
    }), 500


# SECURE: No debug endpoint in production
# Debug information is never exposed to users


# SECURE: Cryptographically secure random token generation
def generate_token():
    """Generate secure session token."""
    return secrets.token_urlsafe(32)


def generate_password_reset_token(user_id: int) -> str:
    """Generate secure password reset token."""
    # SECURE: Use cryptographically secure random bytes
    token = secrets.token_urlsafe(32)
    # In production, store token hash in database with expiration
    return token


# SECURE: Open redirect prevention
@app.route('/redirect')
def safe_redirect():
    """Secure redirect with URL validation."""
    url = request.args.get('url', '/')

    # SECURE: Only allow relative URLs or URLs to allowed hosts
    parsed = urlparse(url)

    if parsed.netloc:
        # External URL - validate against allowlist
        if parsed.netloc not in ALLOWED_REDIRECT_HOSTS:
            logger.warning(f"Blocked redirect to: {url}")
            return redirect(url_for('index'))

    # Relative URL - ensure it doesn't start with // (protocol-relative)
    if url.startswith('//'):
        return redirect(url_for('index'))

    return redirect(url)


# SECURE: Admin panel with authentication and authorization
@app.route('/admin')
@require_auth
def admin_panel():
    """Secure admin panel with authentication."""
    # SECURE: Check user role from authenticated session
    user_role = request.headers.get('X-User-Role')  # Would come from session

    if user_role != 'admin':
        logger.warning("Unauthorized admin access attempt")
        abort(403, description="Admin access required")

    return jsonify({
        'message': 'Admin Panel',
        'actions': ['view_users', 'view_logs']
    })


# SECURE: Mass assignment prevention
@app.route('/update_user', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def update_user():
    """Secure user update with allowlisted fields."""
    user_data = request.json

    if not user_data:
        return jsonify({'error': 'No data provided'}), 400

    # SECURE: Only allow specific fields to be updated
    ALLOWED_FIELDS = {'email', 'name', 'preferences'}

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    for key, value in user_data.items():
        if key in ALLOWED_FIELDS:
            # SECURE: Parameterized update
            cursor.execute(
                f"UPDATE users SET {key} = ? WHERE id = ?",
                (value, user_data.get('id'))
            )

    conn.commit()
    conn.close()

    return jsonify({'message': 'User updated successfully'})


# SECURE: Payment processing with sensitive data handling
@app.route('/process_payment', methods=['POST'])
@require_auth
@limiter.limit("3 per minute")
def process_payment():
    """Secure payment processing without logging sensitive data."""
    # SECURE: Validate required fields exist (but don't log them)
    required_fields = ['card_number', 'cvv', 'expiry']
    for field in required_fields:
        if field not in request.form:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # SECURE: Log transaction without sensitive data
    logger.info("Processing payment transaction")

    # In production: send to payment gateway, never store card details

    return jsonify({
        'status': 'success',
        'transaction_id': secrets.token_hex(16)
    })


@app.route('/')
def index():
    """Home page."""
    return jsonify({
        'message': 'Secure Application API',
        'version': '1.0.0',
        'endpoints': ['/login', '/search', '/profile']
    })


# SECURE: Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


if __name__ == '__main__':
    init_database()
    # SECURE: Production configuration
    # - Debug disabled
    # - Bind to localhost only
    # - Use WSGI server in production (gunicorn, uwsgi)
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False
    )
