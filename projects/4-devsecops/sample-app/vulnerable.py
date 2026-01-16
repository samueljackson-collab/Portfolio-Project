#!/usr/bin/env python3
"""
INTENTIONALLY VULNERABLE APPLICATION - FOR SECURITY TESTING ONLY

This application demonstrates common security vulnerabilities for educational
purposes and security scanner testing. DO NOT use any of this code in production.

Vulnerabilities included:
- SQL Injection (CWE-89)
- Command Injection (CWE-78)
- Cross-Site Scripting (CWE-79)
- Hardcoded Credentials (CWE-798)
- Insecure Deserialization (CWE-502)
- Path Traversal (CWE-22)
- Weak Cryptography (CWE-327)
- Sensitive Data Exposure (CWE-200)
- XML External Entity (CWE-611)
- Server-Side Request Forgery (CWE-918)
"""

import os
import pickle
import hashlib
import subprocess
import sqlite3
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from flask import Flask, request, render_template_string

app = Flask(__name__)

# VULNERABILITY: Hardcoded credentials (CWE-798)
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-secret-api-key-12345"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


def init_database():
    """Initialize SQLite database with sample data."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, password, email, role)
        VALUES (1, 'admin', 'admin123', 'admin@example.com', 'admin')
    ''')
    conn.commit()
    conn.close()


# VULNERABILITY: SQL Injection (CWE-89)
@app.route('/login', methods=['POST'])
def login():
    """Login endpoint vulnerable to SQL injection."""
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # VULNERABLE: Direct string concatenation in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()

    if user:
        return f"Welcome, {username}!"
    return "Invalid credentials"


# VULNERABILITY: Command Injection (CWE-78)
@app.route('/ping')
def ping():
    """Ping endpoint vulnerable to command injection."""
    host = request.args.get('host', 'localhost')

    # VULNERABLE: User input directly in shell command
    result = os.popen(f"ping -c 1 {host}").read()
    return f"<pre>{result}</pre>"


# VULNERABILITY: Another Command Injection variant
@app.route('/lookup')
def dns_lookup():
    """DNS lookup vulnerable to command injection."""
    domain = request.args.get('domain', '')

    # VULNERABLE: subprocess with shell=True and user input
    result = subprocess.run(
        f"nslookup {domain}",
        shell=True,
        capture_output=True,
        text=True
    )
    return f"<pre>{result.stdout}</pre>"


# VULNERABILITY: Cross-Site Scripting - Reflected XSS (CWE-79)
@app.route('/search')
def search():
    """Search endpoint vulnerable to XSS."""
    query = request.args.get('q', '')

    # VULNERABLE: User input directly rendered in HTML
    html = f"""
    <html>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {query}</p>
        <p>No results found.</p>
    </body>
    </html>
    """
    return render_template_string(html)


# VULNERABILITY: Stored XSS via template injection
@app.route('/profile')
def profile():
    """Profile page vulnerable to template injection."""
    name = request.args.get('name', 'Guest')

    # VULNERABLE: User input in template string
    template = f"""
    <html>
    <body>
        <h1>User Profile</h1>
        <p>Name: {name}</p>
        <p>Welcome to your profile page!</p>
    </body>
    </html>
    """
    return render_template_string(template)


# VULNERABILITY: Insecure Deserialization (CWE-502)
@app.route('/load_session', methods=['POST'])
def load_session():
    """Session loading vulnerable to insecure deserialization."""
    session_data = request.form.get('session', '')

    # VULNERABLE: Deserializing untrusted data with pickle
    try:
        import base64
        decoded = base64.b64decode(session_data)
        session = pickle.loads(decoded)
        return f"Session loaded: {session}"
    except Exception as e:
        return f"Error: {e}"


# VULNERABILITY: Path Traversal (CWE-22)
@app.route('/download')
def download():
    """File download vulnerable to path traversal."""
    filename = request.args.get('file', '')

    # VULNERABLE: No validation of file path
    filepath = f"/var/www/files/{filename}"

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {e}"


# VULNERABILITY: Another path traversal variant
@app.route('/view')
def view_file():
    """View file with path traversal vulnerability."""
    doc = request.args.get('doc', 'readme.txt')

    # VULNERABLE: User can traverse directories
    base_path = os.path.join('/var/www/documents', doc)

    with open(base_path, 'r') as f:
        return f.read()


# VULNERABILITY: Weak Cryptography (CWE-327)
def hash_password_weak(password):
    """Hash password using weak algorithm."""
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_sha1(password):
    """Hash password using SHA1."""
    # VULNERABLE: SHA1 is deprecated for security purposes
    return hashlib.sha1(password.encode()).hexdigest()


def encrypt_data_weak(data, key):
    """Encrypt data using weak method."""
    # VULNERABLE: XOR encryption is trivially broken
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))


# VULNERABILITY: XML External Entity (XXE) (CWE-611)
@app.route('/parse_xml', methods=['POST'])
def parse_xml():
    """XML parser vulnerable to XXE."""
    xml_data = request.data.decode('utf-8')

    # VULNERABLE: XML parsing without disabling external entities
    tree = ET.fromstring(xml_data)
    return f"Parsed: {ET.tostring(tree).decode()}"


# VULNERABILITY: Server-Side Request Forgery (SSRF) (CWE-918)
@app.route('/fetch')
def fetch_url():
    """URL fetcher vulnerable to SSRF."""
    url = request.args.get('url', '')

    # VULNERABLE: Fetching arbitrary URLs without validation
    try:
        response = urlopen(url)
        return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"


# VULNERABILITY: Information Disclosure (CWE-200)
@app.route('/error')
def trigger_error():
    """Endpoint that exposes sensitive error information."""
    try:
        # Intentionally cause an error
        result = 1 / 0
    except Exception as e:
        # VULNERABLE: Exposing stack trace to users
        import traceback
        return f"<pre>Error: {e}\n\nStack trace:\n{traceback.format_exc()}</pre>"


# VULNERABILITY: Debug mode enabled in production
@app.route('/debug')
def debug_info():
    """Debug endpoint exposing sensitive information."""
    # VULNERABLE: Exposing environment variables and configuration
    debug_data = {
        'environment': dict(os.environ),
        'database_password': DATABASE_PASSWORD,
        'api_key': API_KEY,
        'config': app.config
    }
    return str(debug_data)


# VULNERABILITY: Insecure random number generation
import random

def generate_token():
    """Generate session token insecurely."""
    # VULNERABLE: Using random instead of secrets for security tokens
    return ''.join(random.choice('abcdef0123456789') for _ in range(32))


def generate_password_reset_token(user_id):
    """Generate password reset token insecurely."""
    # VULNERABLE: Predictable token generation
    return hashlib.md5(f"{user_id}{random.random()}".encode()).hexdigest()


# VULNERABILITY: Hardcoded encryption key
ENCRYPTION_KEY = "supersecretkey123"  # VULNERABLE: Hardcoded key


# VULNERABILITY: Open redirect
@app.route('/redirect')
def open_redirect():
    """Redirect endpoint vulnerable to open redirect."""
    url = request.args.get('url', '/')

    # VULNERABLE: Redirecting to user-supplied URL without validation
    from flask import redirect
    return redirect(url)


# VULNERABILITY: Missing authentication
@app.route('/admin')
def admin_panel():
    """Admin panel without authentication."""
    # VULNERABLE: No authentication check
    return """
    <html>
    <body>
        <h1>Admin Panel</h1>
        <a href="/admin/delete_user?id=1">Delete User</a>
        <a href="/admin/reset_database">Reset Database</a>
    </body>
    </html>
    """


# VULNERABILITY: Mass assignment
@app.route('/update_user', methods=['POST'])
def update_user():
    """Update user vulnerable to mass assignment."""
    user_data = request.json

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # VULNERABLE: Allowing update of any field including 'role'
    for key, value in user_data.items():
        cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_data.get('id')))

    conn.commit()
    conn.close()
    return "User updated"


# VULNERABILITY: Logging sensitive data
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route('/process_payment', methods=['POST'])
def process_payment():
    """Payment processing that logs sensitive data."""
    card_number = request.form.get('card_number', '')
    cvv = request.form.get('cvv', '')

    # VULNERABLE: Logging credit card information
    logger.info(f"Processing payment with card: {card_number}, CVV: {cvv}")

    return "Payment processed"


if __name__ == '__main__':
    init_database()
    # VULNERABLE: Debug mode enabled, binding to all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
